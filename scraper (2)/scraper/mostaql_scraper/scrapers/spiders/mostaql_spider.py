import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import re
import scrapy
from scrapers.items import ProjectItem
from scrapers.utils import convert_utc_to_local, extract_keywords

def clean(t): return re.sub(r"\s+", " ", t or "").strip()

def get_meta(response, label):
    for row in response.css(".meta-row, table tr"):
        lbl = clean(row.css(".meta-label::text, th::text, td:first-child::text").get(""))
        if label in lbl:
            return clean(" ".join(row.css(".meta-value ::text, td:last-child ::text").getall()))
    return ""

class MostaqlSpider(scrapy.Spider):
    name = "mostaql"
    allowed_domains = ["mostaql.com"]
    output_filename = "mostaql_projects.json"
    start_urls = [
        "https://mostaql.com/projects",
        "https://mostaql.com/projects?page=2",
    ]
    custom_settings = {"DOWNLOAD_DELAY": 0.5, "CONCURRENT_REQUESTS": 4}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_urls = set()

    def parse(self, response):
        for row in response.css("tr.project-row"):
            a = row.css("h2 a, h3 a")
            url = response.urljoin(a.attrib.get("href", ""))
            if url and url not in self.seen_urls:
                self.seen_urls.add(url)
                yield response.follow(url, self.parse_project, dont_filter=True, meta={
                    "title": clean(a.css("::text").get("")),
                    "url": url,
                    "time": row.css("time::attr(datetime)").get(""),
                    "brief": clean(" ".join(row.css("p.project__brief ::text").getall())),
                })

    def parse_project(self, response):
        m = response.meta
        item = ProjectItem(platform="مستقل (Mostaql)", url=m["url"])
        title = clean(" ".join(response.css("h1 ::text").getall())) or m["title"]
        item["title"] = title

        # 1. حالة المشروع بدقة (مفتوح / تحت التنفيذ / مكتمل)
        raw_status = get_meta(response, "حالة المشروع") or clean(response.css(".project__status ::text, .badge ::text").get(""))
        status = "مفتوح"
        if any(w in raw_status for w in ["مكتمل", "مغلق", "ملغي", "منتهي"]):
            status = "مكتمل"
        elif any(w in raw_status for w in ["قيد التنفيذ", "تحت التنفيذ", "جاري"]):
            status = "تحت التنفيذ"
        elif any(w in raw_status for w in ["تلقي العروض", "مفتوح"]):
            status = "مفتوح"
        item["status"] = status

        # 2. السعر (إن وُجد فقط دون أي مبالغ وهمية)
        price = clean(response.css('[data-type="project-budget_range"] span::text').get("")) or get_meta(response, "الميزانية")
        if price:
            item["price"] = price

        # 3. مدة التنفيذ
        dur = get_meta(response, "مدة التنفيذ")
        if dur:
            item["duration"] = dur

        # 4. تاريخ النشر
        t = response.css(".meta-row time::attr(datetime)").get("") or m["time"]
        if t:
            item["published_at"] = convert_utc_to_local(clean(t))

        # 5. استخراج تفاصيل المشروع كاملة بدون قسم العروض (#bids مستبعد كلياً)
        desc = ""
        for selector in [
            "#project-brief div.text-wrapper ::text",
            "#project-brief ::text",
            ".project__brief div.text-wrapper ::text",
            ".project__brief ::text",
            ".project-brief ::text",
            ".panel-body > div.text-wrapper ::text",
        ]:
            parts = [clean(p) for p in response.css(selector).getall() if clean(p)]
            if parts:
                desc = clean(" ".join(parts))
                break

        if not desc or len(desc) < 20:
            desc = m["brief"]

        # إزالة عنوان الترويسة الشائع "تفاصيل المشروع" إن وجد في البداية
        desc = re.sub(r"^تفاصيل المشروع\s*", "", desc).strip()
        item["brief"] = desc
        item["description"] = desc

        # 6. استخراج المهارات والكلمات المفتاحية بدقة عالية
        raw_skills = [clean(s) for s in response.css(".skills__item bdi::text, .tag bdi::text, .skills-item ::text, a[href*='/skills/'] ::text").getall()]
        keywords = extract_keywords(title=title, text=desc, existing_tags=raw_skills)
        item["requirements"] = keywords

        yield item


if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "scrapers.settings")
    process = CrawlerProcess(get_project_settings())
    process.crawl(MostaqlSpider)
    process.start()
