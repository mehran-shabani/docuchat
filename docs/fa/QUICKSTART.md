# راهنمای شروع سریع DocuChat

DocuChat را در کمتر از ۵ دقیقه راه‌اندازی کنید!

## پیش‌نیازها

- [Docker](https://docs.docker.com/get-docker/) و [Docker Compose](https://docs.docker.com/compose/install/) نسخه ۲
- [کلید API OpenAI](https://platform.openai.com/api-keys) (اختیاری برای تست اولیه)

## 🚀 شروع سریع

### ۱. کلون کردن مخزن

```bash
git clone https://github.com/your-org/docuchat.git
cd docuchat
```

### ۲. پیکربندی محیط

```bash
# کپی کردن فایل نمونه محیط
cp backend/.env.example backend/.env

# ویرایش backend/.env و افزودن کلید API OpenAI
# nano backend/.env
# یا
# vim backend/.env
```

**backend/.env:**
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
DATABASE_URL=postgresql://docuchat:docuchat_pass@postgres:5432/docuchat
```

### ۳. راه‌اندازی تمام سرویس‌ها

```bash
cd infra
docker compose up
```

منتظر بمانید تا تمام سرویس‌ها راه‌اندازی شوند (تقریباً ۲-۳ دقیقه در اجرای اول).

### ۴. تایید نصب

مرورگر خود را باز کرده و به آدرس‌های زیر بروید:

- **فرانت‌اند:** http://localhost:3000
- **API بک‌اند:** http://localhost:8000
- **مستندات API:** http://localhost:8000/docs
- **بررسی سلامت:** http://localhost:8000/healthz

باید موارد زیر را ببینید:
- فرانت‌اند: رابط کاربری زیبا با پشتیبانی راست‌به‌چپ فارسی با نوشته "DocuChat is live"
- بررسی سلامت: `{"status":"ok"}`

### ۵. تست نقطه پایانی دمو

```bash
# تست نقطه پایانی سلامت
curl http://localhost:8000/healthz

# تست دمو چت هوش مصنوعی (نیاز به OPENAI_API_KEY دارد)
curl http://localhost:8000/v1/chat/demo
```

پاسخ مورد انتظار:
```json
{"reply": "pong"}
```

## 🛠️ حالت توسعه

### توسعه بک‌اند

```bash
cd backend

# ایجاد محیط مجازی (در صورت نصب بودن بسته venv)
python3 -m venv venv
source venv/bin/activate  # در ویندوز: venv\Scripts\activate

# نصب وابستگی‌ها
pip install -r requirements.txt

# اجرای سرور توسعه با قابلیت بارگذاری مجدد خودکار
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

برای مستندات تعاملی API به آدرس http://localhost:8000/docs بروید.

### توسعه فرانت‌اند

```bash
cd frontend

# نصب وابستگی‌ها
npm install

# اجرای سرور توسعه با قابلیت بارگذاری مجدد خودکار
npm run dev
```

برای مشاهده تغییرات به صورت زنده به http://localhost:3000 بروید.

## 🧪 اجرای تست‌ها

### تست‌های بک‌اند

```bash
cd backend
pytest -q
```

### بررسی کدنویسی

```bash
# بک‌اند
cd backend
ruff check .
ruff format --check .

# فرانت‌اند
cd frontend
npm run lint
```

## 📁 ساختار پروژه

```
docuchat/
├── backend/              # برنامه FastAPI
│   ├── app/             # کد برنامه
│   │   └── main.py      # برنامه اصلی FastAPI
│   ├── tests/           # مجموعه تست
│   ├── Dockerfile       # کانتینر بک‌اند
│   └── requirements.txt # وابستگی‌های Python
├── frontend/            # برنامه Next.js 14
│   ├── src/            # کد منبع
│   │   ├── pages/      # صفحات Next.js
│   │   └── styles/     # استایل‌های CSS
│   ├── Dockerfile      # کانتینر فرانت‌اند
│   └── package.json    # وابستگی‌های Node
├── infra/              # زیرساخت
│   ├── docker-compose.yml  # پیکربندی Docker Compose
│   ├── helm/          # چارت‌های Helm برای Kubernetes
│   └── terraform/     # زیرساخت به عنوان کد
└── docs/              # مستندات
    ├── en/            # مستندات انگلیسی
    └── fa/            # مستندات فارسی
```

## 🐳 دستورات Docker

```bash
# راه‌اندازی تمام سرویس‌ها در پس‌زمینه
docker compose up -d

# مشاهده لاگ‌ها
docker compose logs -f

# توقف تمام سرویس‌ها
docker compose down

# ساخت مجدد و راه‌اندازی
docker compose up --build

# توقف و حذف حجم‌ها (شروع تازه)
docker compose down -v
```

## 🔧 مشکلات رایج

### پورت در حال استفاده است

اگر پورت‌های ۳۰۰۰، ۵۴۳۲، یا ۸۰۰۰ در حال استفاده هستند:

```bash
# بررسی کنید چه چیزی از پورت استفاده می‌کند
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# گزینه ۱: توقف سرویس متضاد
# گزینه ۲: تغییر پورت‌ها در docker-compose.yml
```

### کلید API OpenAI کار نمی‌کند

```bash
# تایید کنید که کلید API تنظیم شده است
cat backend/.env | grep OPENAI_API_KEY

# تست بدون OpenAI (فقط بررسی سلامت)
curl http://localhost:8000/healthz
```

### دسترسی به Docker رد شد

```bash
# کاربر خود را به گروه docker اضافه کنید (Linux)
sudo usermod -aG docker $USER
# خروج و ورود مجدد
```

## 📚 گام‌های بعدی

1. **کاوش در API**: به http://localhost:8000/docs بروید
2. **خواندن مستندات**: [docs/fa/README.md](./README.md) را بررسی کنید
3. **سفارشی‌سازی فرانت‌اند**: `frontend/src/pages/index.tsx` را ویرایش کنید
4. **افزودن نقاط پایانی**: `backend/app/main.py` را ویرایش کنید
5. **استقرار در محیط تولید**: [docs/en/DEPLOYMENT.md](../en/DEPLOYMENT.md) را ببینید

## 🤝 دریافت کمک

- **مستندات**: [docs/fa/README.md](./README.md)
- **مسائل**: [GitHub Issues](https://github.com/your-org/docuchat/issues)
- **بحث‌ها**: [GitHub Discussions](https://github.com/your-org/docuchat/discussions)

## 🎉 آماده هستید!

اکنون یک نمونه کاملاً کاربردی DocuChat به صورت محلی در حال اجرا دارید. کدنویسی خوشحال!

---

**به کمک بیشتری نیاز دارید؟** [مستندات کامل](./README.md) را بررسی کنید یا یک [issue](https://github.com/your-org/docuchat/issues) باز کنید.
