import re
from datetime import datetime, timedelta


def get_local_utc_offset() -> timedelta:
    offset = datetime.now().astimezone().utcoffset()
    return offset if offset is not None else timedelta(hours=3)


def convert_utc_to_local(utc_str: str) -> str:
    if not utc_str:
        return ""
    try:
        dt = datetime.strptime(utc_str.strip()[:19], "%Y-%m-%d %H:%M:%S")
        return (dt + get_local_utc_offset()).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return utc_str


def parse_arabic_relative_time(text: str, now: datetime = None) -> str:
    if not text:
        return ""
    now = now or datetime.now()
    t = re.sub(r"^\s*منذ\s*", "", text.strip())
    total = 0

    sec = re.search(r"(\d+)\s*(?:ثانية|ثواني|ثوانٍ)", t)
    if sec:
        total += int(sec.group(1))
    elif "لحظات" in t:
        total += 30

    m = re.search(r"(\d+)\s*(?:دقيقة|دقائق)", t)
    if m:
        total += int(m.group(1)) * 60
    elif "دقيقتين" in t:
        total += 120
    elif "دقيقة" in t:
        total += 60

    h = re.search(r"(\d+)\s*(?:ساعة|ساعات)", t)
    if h:
        total += int(h.group(1)) * 3600
    elif "ساعتين" in t:
        total += 7200
    elif "ساعة" in t:
        total += 3600

    d = re.search(r"(\d+)\s*(?:يوم|أيام|ايام)", t)
    if d:
        total += int(d.group(1)) * 86400
    elif "يومين" in t:
        total += 172800
    elif "يوم" in t:
        total += 86400

    w = re.search(r"(\d+)\s*(?:أسبوع|أسابيع|اسبوع)", t)
    if w:
        total += int(w.group(1)) * 604800
    elif "أسبوعين" in t or "اسبوعين" in t:
        total += 1209600
    elif "أسبوع" in t or "اسبوع" in t:
        total += 604800

    mo = re.search(r"(\d+)\s*(?:شهر|أشهر|اشهر)", t)
    if mo:
        total += int(mo.group(1)) * 2592000
    elif "شهرين" in t:
        total += 5184000
    elif "شهر" in t:
        total += 2592000

    return (now - timedelta(seconds=total)).strftime("%Y-%m-%d %H:%M:%S")


# =====================================================================
# Intelligent Skill & Keyword Extractor
# =====================================================================

DOMAIN_SKILLS_EN = [
    # Frontend & Web
    "React", "React.js", "Next.js", "Vue", "Vue.js", "Angular", "TypeScript", "JavaScript",
    "HTML5", "CSS3", "Tailwind CSS", "Bootstrap", "Sass", "WordPress", "Shopify", "WooCommerce",
    "Webflow", "Wix", "PHP", "Laravel", "Symfony", "Ruby on Rails",
    # Backend & Languages
    "Python", "FastAPI", "Django", "Flask", "Node.js", "Express.js", "NestJS", "Java", "Spring Boot",
    "C#", ".NET", "ASP.NET", "C++", "C", "Go", "Rust", "PHP",
    # Mobile
    "Flutter", "Dart", "React Native", "Android", "iOS", "Swift", "Kotlin", "Mobile App Development",
    # Data, AI & Automation
    "AI", "Machine Learning", "Deep Learning", "NLP", "OpenAI", "ChatGPT", "LLM", "n8n", "Zapier",
    "Make", "Automation", "Process Automation", "Web Scraping", "Scrapy", "Selenium", "BeautifulSoup",
    "Pandas", "NumPy", "Power BI", "Tableau", "Excel", "Data Analysis", "Data Entry", "Chatbot",
    # Databases & DevOps
    "PostgreSQL", "MySQL", "MongoDB", "Firebase", "Supabase", "Redis", "SQLite", "SQL",
    "Docker", "Kubernetes", "AWS", "Google Cloud", "Azure", "Linux", "Git", "GitHub", "CI/CD",
    # Design & Media
    "UI/UX", "UI/UX Design", "Figma", "Adobe XD", "Photoshop", "Adobe Illustrator", "Graphic Design",
    "Logo Design", "Branding", "Video Editing", "Adobe Premiere", "After Effects", "Motion Graphics",
    "3D Modeling", "Blender", "Canva",
    # Marketing & Content
    "SEO", "SEM", "Google Ads", "Facebook Ads", "Digital Marketing", "Social Media Marketing",
    "Copywriting", "Content Writing", "Translation", "Proofreading", "Transcription", "Virtual Assistant"
]

DOMAIN_SKILLS_AR = [
    # البرمجة والتطوير
    "تطوير الويب", "برمجة المواقع", "برمجة تطبيقات", "تطوير التطبيقات", "رياكت", "بايثون",
    "ووردبريس", "شوبيفاي", "لارفيل", "فلاتر", "واجهة أمامية", "واجهة خلفية", "قواعد بيانات",
    # الذكاء الاصطناعي والأتمتة
    "الذكاء الاصطناعي", "أتمتة العمليات", "أتمتة n8n", "شات بوت", "استخراج بيانات", "تحليل بيانات",
    # التصميم والميديا
    "تصميم UI/UX", "تصميم واجهات", "تصميم جرافيك", "تصميم شعار", "هوية بصرية", "موشن جرافيك",
    "مونتاج فيديو", "تعديل فيديو", "فوتوشوب", "إليستريتور", "فيجما", "تصميم إعلانات", "رسم رقمي",
    # التسويق والمحتوى والترجمة
    "سيو (SEO)", "التسويق الإلكتروني", "إعلانات جوجل", "إعلانات فيسبوك", "إدارة حسابات",
    "كتابة محتوى", "كتابة إبداعية", "صناعة محتوى", "الترجمة", "تدقيق لغوي", "تفريغ صوتي",
    "إدخال بيانات", "مايكروسوفت إكسيل", "محاسبة مالية", "دراسة جدوى", "تعليق صوتي"
]

AR_STOP_WORDS = {
    "مطلوب", "أريد", "اريد", "ابحث", "أبحث", "عمل", "مشروع", "خدمة", "بناء", "إنشاء",
    "انشاء", "تصميم", "برمجة", "طريقة", "محترف", "متخصص", "خبرة", "السلام", "عليكم",
    "ورحمة", "الله", "وبركاته", "شكرا", "شكراً", "تحية", "طيبة", "وبعد", "خلال", "داخل",
    "خارج", "موقع", "صفحة", "مواقع", "تطبيق", "برنامج", "نظام", "منصة", "شركة", "شخص",
    "فقط", "بشكل", "كامل", "سريع", "ممتاز", "جيد", "جديد", "سعر", "ميزانية", "وقت",
    "يوم", "ايام", "ساعة", "شهر", "التفاصيل", "تفاصيل", "المطلوب", "التواصل", "الخاص"
}


def extract_keywords(title: str = "", text: str = "", existing_tags: list = None) -> list:
    """
    Intelligently extracts, normalizes, and ranks keywords & skills
    from job title, description, and existing tags.
    """
    extracted = []
    seen_lower = set()

    def add_keyword(kw: str):
        kw_clean = re.sub(r"[\s_]+", " ", str(kw or "")).strip()
        kw_clean = re.sub(r"^[-–—•*#\d\.\s]+", "", kw_clean)
        if not kw_clean or len(kw_clean) < 2 or len(kw_clean) > 35:
            return
        if kw_clean.lower() in seen_lower:
            return
        if kw_clean.lower() in AR_STOP_WORDS:
            return
        seen_lower.add(kw_clean.lower())
        extracted.append(kw_clean)

    # 1. First Priority: Explicit platform tags
    if existing_tags:
        for tag in existing_tags:
            if isinstance(tag, str):
                for part in re.split(r"[,/؛|،]+", tag):
                    add_keyword(part.strip())

    corpus = f" {title} {text} "
    corpus_lower = corpus.lower()

    # 2. Match known English tech/domain keywords
    for skill in DOMAIN_SKILLS_EN:
        pattern = r'(?<![a-zA-Z0-9_])' + re.escape(skill.lower()) + r'(?![a-zA-Z0-9_])'
        if re.search(pattern, corpus_lower):
            add_keyword(skill)

    # 3. Match known Arabic skills
    for skill in DOMAIN_SKILLS_AR:
        if skill in corpus:
            add_keyword(skill)

    # 4. If still few keywords, extract distinctive words from title
    if len(extracted) < 4 and title:
        words = re.findall(r"[\w\u0600-\u06FF\+#\.]+", title)
        for w in words:
            if len(w) >= 3 and w.lower() not in AR_STOP_WORDS and not w.isdigit():
                add_keyword(w)
            if len(extracted) >= 7:
                break

    # Return top 4-8 clean keywords
    return extracted[:8]
