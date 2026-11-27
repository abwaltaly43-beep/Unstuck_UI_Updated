# 🚀 Freelance Scrapers Dynamic API & n8n Automation (PostgreSQL Upsert)
### نظام سحب ومتابعة مشاريع منصات العمل الحر مع التخزين في PostgreSQL والتكامل مع n8n

نظام متكامل ومبسّط مبني بلغة بايثون و **Scrapy** مع واجهة برمجية سريعة وخفيفة باستخدام **FastAPI**، ونظام تخزين وحفظ فوري في قاعدة بيانات **PostgreSQL** يدعم تقنية **UPSERT** لمنع تكرار البيانات وتحديث المشاريع لحظياً أولاً بأول.

يجمع النظام أحدث المشاريع المنشورة من **4 منصات رئيسية**:
1. 🟢 **مستقل (Mostaql)**
2. 🟠 **خمسات (Khamsat)**
3. 🔵 **نفذلي (Nafezly)**
4. 🔷 **Freelancer.com**

---

## 📁 هيكل مجلد المشروع (Project Structure)

```text
mostaql_scraper/
│
├── scrapers/                       # حزمة Scrapy المركزية
│   ├── spiders/                    # ملفات السبايدر لكل منصة
│   │   ├── mostaql_spider.py
│   │   ├── khamsat_spider.py
│   │   ├── nafezly_spider.py
│   │   └── freelancer_spider.py
│   ├── items.py                    # تعريف بنية بيانات المشاريع (ProjectItem)
│   ├── database.py                 # اتصال PostgreSQL وعمليات UPSERT والاستعلامات
│   ├── pipelines.py                # Pipeline للتخزين الفوري في DB والترتيب في JSON
│   ├── settings.py                 # إعدادات Scrapy والـ Pipelines
│   └── utils.py                    # معالجة التوقيت النسبي والتحويل للتوقيت المحلي
│
├── output/                         # مجلد مخرجات ملفات الـ JSON (نسخ احتياطية)
├── main.py                         # خادم FastAPI مع دعم القراءة المباشرة من DB
├── run.py                          # سكريبت تشغيل السكرابر المباشر محلياً
├── import_json_to_db.py            # سكريبت استيراد ملفات الـ JSON السابقة إلى PostgreSQL
├── docker-compose.yml              # تشغيل PostgreSQL بضغطة زر عبر Docker
├── .env.example                    # نموذج إعدادات الاتصال بقاعدة البيانات
├── .env                            # إعدادات الاتصال الخاصة بك
├── n8n_workflow.json               # ملف الورك فلو الجاهز للاستيراد داخل n8n
├── requirements.txt                # متطلبات ومكتبات بايثون المطلوبة
│
├── INSTALL_REQUIREMENTS.bat        # ملف باتش: تثبيت كافة المتطلبات بضغطة واحدة
└── START_API.bat                   # ملف باتش: تشغيل خادم FastAPI مباشرة
```

---

## 🐘 تشغيل وإعداد PostgreSQL

### الخيار 1: عبر Docker (الأسهل والأسرع)
إذا كان لديك **Docker Desktop**، شغل الأمر التالي داخل المجلد:
```bash
docker compose up -d
```
سيتم تشغيل PostgreSQL تلقائياً على المنفذ `5432` باسم مستخدم `postgres` وباسورد `postgres`.

### الخيار 2: عبر التثبيت المباشر على Windows
تأكد من مطابقة إعدادات الاتصال داخل ملف **`.env`**:
```ini
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

---

## 🔄 ميزة الـ UPSERT (عدم تكرار البيانات)

* تم ربط جدول `projects` بقيد فريد على حقل الرابط: `UNIQUE (url)`.
* عند تشغيل السكرابر، يتم تنفيذ:
  ```sql
  INSERT INTO projects (...) VALUES (...)
  ON CONFLICT (url) DO UPDATE SET ...
  ```
* **المشاريع الجديدة:** تُضاف فوراً في الجدول.
* **المشاريع الموجودة مسبقاً:** يتم تحديث بياناتها وتوقيت `updated_at` دون مضاعفة السجلات.

---

## 📥 استيراد المشاريع السابقة إلى PostgreSQL

إذا كان لديك مشاريع مخزنة مسبقاً في مجلد `output/*.json` وتريد نقلها فوراً إلى قاعدة البيانات:
```bash
py import_json_to_db.py
```

---

## ⚡ التشغيل السريع (Quick Start Guide)

### 1️⃣ الخطوة الأولى: تثبيت المتطلبات
اضغط مرتين على: 👉 **`INSTALL_REQUIREMENTS.bat`**  
أو عبر سطر الأوامر:
```bash
py -m pip install -r requirements.txt
```

### 2️⃣ الخطوة الثانية: تشغيل خادم الـ API
اضغط مرتين على: 👉 **`START_API.bat`**  
- 📖 **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- 📊 **حالة النظام والـ DB:** [http://localhost:8000/api/status](http://localhost:8000/api/status)
- 🩺 **فحص اتصال الـ DB:** [http://localhost:8000/api/db-status](http://localhost:8000/api/db-status)

---

## 🕷️ تشغيل السكرابر المباشر محلياً (`run.py`)

```bash
# سحب جميع المنصات الأربعة معاً والتخزين في PostgreSQL فوراً
py run.py

# أو سحب منصة محددة فقط:
py run.py --spider mostaql     # مستقل فقط
py run.py --spider khamsat     # خمسات فقط
py run.py --spider nafezly     # نفذلي فقط
py run.py --spider freelancer  # فريلانسر فقط
```

---

## 🧩 تشغيل الورك فلو في n8n (`n8n_workflow.json`)

1. افتح **n8n**.
2. اختر **Import from File** واختر **`n8n_workflow.json`**.
3. إذا كان n8n يعمل عبر Docker، سيتصل تلقائياً بالـ API عبر `http://host.docker.internal:8000`.
4. يمكنك أيضاً إضافة عقدة PostgreSQL مباشرة داخل n8n والاستعلام من جدول `projects` بكل سهولة.
