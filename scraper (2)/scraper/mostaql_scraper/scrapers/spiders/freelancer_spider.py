import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import json, re
from datetime import datetime
import scrapy
from scrapers.items import ProjectItem
from scrapers.utils import convert_utc_to_local, extract_keywords

def clean(t): return re.sub(r"\s+", " ", t or "").strip()

class FreelancerSpider(scrapy.Spider):
    name = "freelancer"
    allowed_domains = ["freelancer.com"]
    output_filename = "freelancer_projects.json"
    # full_description=true guarantees complete, unabridged project details without proposals
    start_urls = ["https://www.freelancer.com/api/projects/0.1/projects/active?limit=60&full_description=true&job_details=true"]
    custom_settings = {"DOWNLOAD_DELAY": 0.5}

    def parse(self, response):
        try:
            data = json.loads(response.text)
        except Exception:
            return

        for p in data.get("result", {}).get("projects", []):
            item = ProjectItem(platform="فريلانسر (Freelancer.com)")
            title = clean(p.get("title", ""))
            item["title"] = title

            seo = p.get("seo_url")
            item["url"] = f"https://www.freelancer.com/projects/{seo or p.get('id')}"

            # 1. حالة المشروع باللغة الإنجليزية كما طُلب صراحة: Open / In Progress / Completed
            raw_st = str(p.get("status", "")).lower()
            sub_st = str(p.get("sub_status", "")).lower()
            status = "Open"
            if raw_st in ["closed", "complete", "frozen"] or sub_st in ["closed", "complete"]:
                status = "Completed"
            elif raw_st in ["pending", "in_progress", "custom"] or sub_st in ["pending", "in_progress"]:
                status = "In Progress"
            elif raw_st in ["active", "open"]:
                status = "Open"
            item["status"] = status

            # 2. السعر الحقيقي فقط (بدون أي مبالغ وهمية)
            sign = p.get("currency", {}).get("sign", "$")
            code = p.get("currency", {}).get("code", "USD")
            lo = p.get("budget", {}).get("minimum")
            hi = p.get("budget", {}).get("maximum")
            if lo and hi:
                item["price"] = f"{sign}{lo} - {sign}{hi} {code}"
            elif lo:
                item["price"] = f"{sign}{lo} {code}"

            # 3. المدة إن وجدت
            if p.get("bidperiod"):
                item["duration"] = f"{p['bidperiod']} Days"

            # 4. تاريخ النشر
            ts = p.get("submitdate") or p.get("time_submitted")
            if ts:
                try:
                    item["published_at"] = convert_utc_to_local(datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M:%S"))
                except Exception:
                    pass

            # 5. تفاصيل الوظيفة الكاملة بدون العروض (Full Project Details)
            full_desc = clean(p.get("description") or p.get("preview_description") or "")
            if not full_desc:
                full_desc = title
            item["brief"] = full_desc
            item["description"] = full_desc

            # 6. استخراج الكلمات المفتاحية والمهارات بدقة
            raw_skills = [clean(j.get("name", "")) for j in p.get("jobs", []) if j.get("name")]
            keywords = extract_keywords(title=title, text=full_desc, existing_tags=raw_skills)
            item["requirements"] = keywords

            yield item


if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "scrapers.settings")
    process = CrawlerProcess(get_project_settings())
    process.crawl(FreelancerSpider)
    process.start()
