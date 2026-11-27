import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import re
import scrapy
from scrapers.items import ProjectItem
from scrapers.utils import parse_arabic_relative_time, extract_keywords

def clean(t): return re.sub(r"\s+", " ", t or "").strip()

class KhamsatSpider(scrapy.Spider):
    name = "khamsat"
    allowed_domains = ["khamsat.com"]
    output_filename = "khamsat_projects.json"
    start_urls = [
        "https://khamsat.com/community/requests",
        "https://khamsat.com/community/requests?page=2",
    ]
    custom_settings = {
        "DOWNLOAD_DELAY": 0.5,
        "CONCURRENT_REQUESTS": 4
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_urls = set()

    def parse(self, response):
        for row in response.css("tr.forum_post"):
            a = row.css("h3.details-head a")
            title = re.sub(r"^عنوان الطلب:\s*", "", clean(a.css("::text").get("")))
            href = a.attrib.get("href", "")
            if not title or not href:
                continue

            url = response.urljoin(href)
            if url in self.seen_urls:
                continue
            self.seen_urls.add(url)

            # وقت النشر الأصلي للطلب (تجنب وقت آخر تفاعل للمعلقين)
            raw_time = next((clean(t) for t in row.css("ul.details-list span ::text, ul.details-list li ::text").getall()
                             if clean(t).startswith("منذ") and "تفاعل" not in clean(t)), "")
            if not raw_time:
                raw_time = next((clean(t) for t in row.css("span ::text, td ::text").getall()
                                 if clean(t).startswith("منذ") and "تفاعل" not in clean(t)), "")

            published_at = parse_arabic_relative_time(raw_time) or raw_time if raw_time else None

            # الحالة: طلبات مجتمع خمسات المفتوحة
            row_text = clean(" ".join(row.css("h3.details-head ::text, .badge ::text, .label ::text").getall()))
            status = "مفتوح"
            if any(w in row_text for w in ["مكتمل", "تم الشراء", "تم الاتفاق", "تم التنفيذ", "مغلق", "ملغي"]):
                status = "مكتمل"
            elif any(w in row_text for w in ["قيد التنفيذ", "تحت التنفيذ", "جاري التنفيذ"]):
                status = "تحت التنفيذ"

            # استخراج السعر إن ذُكر صراحة فقط، وإن لم يوجد لا تضع أي قيمة افتراضية
            price = None
            price_match = re.search(
                r'(?:ميزاني[ةي]|الميزانية|سعر|السعر|مقابل|بـ|بمبلغ|مبلغ|تكلفة)\s*[:=]?\s*(\$?\s*\d+(?:\s*[-–]\s*\d+)?\s*(?:\$|دولار|USD)?)',
                title,
                re.IGNORECASE
            )
            if price_match:
                price = clean(price_match.group(1))

            # المدة إن ذُكرت صراحة
            duration = None
            dur_match = re.search(
                r'(?:خلال|في غضون|مدة|المدة|في)\s*(\d+\s*(?:يوم|أيام|ايام|ساعة|ساعات|أسبوع|اسبوع|اسابيع|شهر)|يومين|اسبوعين|شهرين)',
                title
            )
            if dur_match:
                duration = clean(dur_match.group(1))

            keywords = extract_keywords(title=title, text=title)

            # ملاحظة: صفحات تفاصيل خمسات (/community/requests/<id>) محمية بـ AWS WAF Challenge،
            # لذلك نعتمد على العنوان الكامل للطلب الأصلي من صفحة القائمة بدون تعليقات البائعين.
            item = ProjectItem(
                platform="خمسات (Khamsat)",
                title=title,
                url=url,
                brief=title,
                description=title,
                status=status,
                requirements=keywords
            )
            if price:
                item["price"] = price
            if duration:
                item["duration"] = duration
            if published_at:
                item["published_at"] = published_at

            yield item


if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "scrapers.settings")
    process = CrawlerProcess(get_project_settings())
    process.crawl(KhamsatSpider)
    process.start()
