import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import json, re
import scrapy
from scrapers.items import ProjectItem
from scrapers.utils import parse_arabic_relative_time, extract_keywords

def clean(t): return re.sub(r"\s+", " ", t or "").strip()

def get_schema(response):
    for script in response.css('script[type*="json"]::text').getall():
        if '"JobPosting"' in script:
            try:
                d = json.loads(script)
                if d.get("@type") == "JobPosting":
                    return d
            except Exception:
                pass
    return {}

def get_desc(response, job):
    # 1. من schema.org JobPosting description (يوفر النص الأصلي بالكامل دون عروض)
    desc = clean(job.get("description", ""))
    if desc and len(desc) > 25:
        return desc

    # 2. من حاوية تفاصيل المشروع مباشرة (مع استبعاد قسم العروض المقدمة تماماً)
    for selector in [
        "#project-content ::text",
        ".project-content ::text",
        ".project-description ::text",
        "[class*='project-details'] ::text",
        "[class*='description'] p::text, [class*='description'] li::text",
    ]:
        parts = [clean(p) for p in response.css(selector).getall() if len(clean(p)) > 10]
        if parts:
            return clean(" ".join(parts))

    # 3. من meta description tag
    desc = clean(response.css('meta[name="description"]::attr(content)').get(""))
    if desc and len(desc) > 30:
        return desc

    # 4. من og:description
    desc = clean(response.css('meta[property="og:description"]::attr(content)').get(""))
    if desc and len(desc) > 30:
        return desc

    return ""


class NafezlySpider(scrapy.Spider):
    name = "nafezly"
    allowed_domains = ["nafezly.com"]
    output_filename = "nafezly_projects.json"
    start_urls = [
        "https://nafezly.com/projects",
        "https://nafezly.com/projects?page=2",
    ]
    custom_settings = {"DOWNLOAD_DELAY": 0.5, "CONCURRENT_REQUESTS": 4}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_urls = set()

    def parse(self, response):
        for a in response.xpath('//a[contains(@href, "/project/")]'):
            url = response.urljoin(a.attrib.get("href", ""))
            if any(c.isdigit() for c in url) and url not in self.seen_urls and not url.endswith("/create-guest"):
                self.seen_urls.add(url)
                yield response.follow(url, self.parse_project, dont_filter=True)

    def parse_project(self, response):
        job = get_schema(response)
        item = ProjectItem(platform="نفذلي (Nafezly)", url=response.url)
        title = clean(job.get("title", "")) or clean(" ".join(response.css("h1 ::text").getall()))
        item["title"] = title

        # 1. تحديد حالة المشروع بدقة (مفتوح / تحت التنفيذ / مكتمل)
        raw_status = ""
        for node in response.xpath('//*[contains(text(),"حالة المشروع") or contains(text(),"الحالة")]/parent::*'):
            raw_status = clean(" ".join(node.css("::text").getall()))
            if raw_status: break

        if not raw_status:
            raw_status = clean(" ".join(response.css(".project-status ::text, .badge ::text, [class*='status'] ::text").getall()))

        status = "مفتوح"
        if any(w in raw_status for w in ["مكتمل", "منتهي", "مغلق", "ملغي"]):
            status = "مكتمل"
        elif any(w in raw_status for w in ["قيد التنفيذ", "تحت التنفيذ", "جاري"]):
            status = "تحت التنفيذ"
        else:
            status = "مفتوح"
        item["status"] = status

        # 2. السعر الحقيقي فقط (بدون أي أرقام وهمية)
        price = ""
        for node in response.xpath('//*[contains(text(),"الميزانية")]/parent::*'):
            m = re.search(r'(\d+(?:\s*[-–]\s*\d+)?\s*\$)', " ".join(node.css("::text").getall()))
            if m: price = clean(m.group(1)); break
        if not price and job.get("baseSalary"):
            val = job["baseSalary"].get("value", {}).get("value")
            if val: price = f"{val} {job.get('salaryCurrency', 'USD')}"
        if price:
            item["price"] = price

        # 3. مدة التنفيذ
        duration = ""
        dur_nodes = response.xpath('//*[contains(text(),"المدة المتاحة") or contains(text(),"مدة التنفيذ")]/parent::*')
        for node in dur_nodes:
            raw_text = clean(" ".join(node.css("::text").getall()))
            m = re.search(r'(\d+)\s*(?:يوم|أيام|ايام|ساعة|ساعات|شهر|أسبوع|اسبوع)', raw_text)
            if m:
                duration = m.group(0)
                break
        if not duration and job.get("workHours"):
            duration = f"{job.get('workHours')} أيام"
        if duration:
            item["duration"] = duration

        # 4. تاريخ النشر
        raw_pub = ""
        for node in response.xpath('//*[contains(text(),"تاريخ النشر")]/parent::*'):
            txts = [t.strip() for t in node.css("::text").getall()
                    if t.strip() and t.strip() != "تاريخ النشر"]
            if txts: raw_pub = " ".join(txts); break
        dt = parse_arabic_relative_time(raw_pub) if raw_pub else (
            f"{clean(job.get('datePosted', ''))} 00:00:00" if job.get("datePosted") else "")
        if dt: item["published_at"] = dt
        elif raw_pub: item["published_at"] = raw_pub

        # 5. تفاصيل المشروع الكاملة بدون قسم العروض (Full Project Details)
        desc = get_desc(response, job)
        if not desc:
            desc = title
        item["brief"] = desc
        item["description"] = desc

        # 6. استخراج المهارات والكلمات المفتاحية بدقة عالية
        raw_s = job.get("skills", [])
        raw_skills = [clean(s) for s in (raw_s.split(",") if isinstance(raw_s, str) else raw_s) if clean(s)]
        if not raw_skills:
            raw_skills = [clean(s) for s in response.css('a[href*="skill"]::text, .tag::text, .badge::text').getall()]
        keywords = extract_keywords(title=title, text=desc, existing_tags=raw_skills)
        item["requirements"] = keywords

        yield item


if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "scrapers.settings")
    process = CrawlerProcess(get_project_settings())
    process.crawl(NafezlySpider)
    process.start()
