# 🚀 راهنمای شروع سریع DocuChat

این راهنما برای شروع سریع کار با پروژه DocuChat است که شامل فرانت‌اند Next.js و بک‌اند FastAPI می‌شود.

## 📋 پیش‌نیازها

- **Node.js** 18+
- **Python** 3.11+
- **pnpm** (برای فرانت‌اند)
- **Docker** (اختیاری برای دیتابیس)

## 🎯 شروع سریع (5 دقیقه)

### 1️⃣ راه‌اندازی بک‌اند

```bash
# رفتن به پوشه بک‌اند
cd backend

# نصب وابستگی‌ها
pip install -r requirements.txt

# اجرای سرور
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

بررسی: `curl http://localhost:8000/healthz`

### 2️⃣ راه‌اندازی فرانت‌اند

```bash
# رفتن به پوشه فرانت‌اند
cd frontend

# نصب وابستگی‌ها
pnpm install

# کپی فایل محیطی
cp .env.local.example .env.local

# اجرای سرور توسعه
pnpm dev
```

باز کردن: http://localhost:3000

## ✅ تست اتصال

1. باز کردن مرورگر: `http://localhost:3000`
2. کلیک روی "شروع چت"
3. تایپ یک پیام: "سلام"
4. بررسی دریافت پاسخ از بک‌اند

## 🔧 تنظیمات پیشرفته

### فعال‌سازی WebSocket

در `frontend/.env.local`:
```env
NEXT_PUBLIC_ENABLE_WS=true
NEXT_PUBLIC_WS_ENDPOINT=ws://localhost:8000/ws/chat
```

**توجه**: WebSocket در بک‌اند فعلی پیاده‌سازی نشده (برای ایجنت ۳)

### تغییر مدل OpenAI

```env
NEXT_PUBLIC_OPENAI_MODEL=gpt-4o
NEXT_PUBLIC_MODEL_OPTIONS=gpt-3.5-turbo,gpt-4o,gpt-4o-mini
```

## 🧪 اجرای تست‌ها

### تست بک‌اند
```bash
cd backend
pytest
```

### تست فرانت‌اند
```bash
cd frontend
pnpm test
```

## 📚 Storybook

برای مشاهده کامپوننت‌ها:

```bash
cd frontend
pnpm story
```

باز کردن: http://localhost:6006

## 🐳 Docker (اختیاری)

```bash
# ساخت و اجرای کل stack
docker-compose up -d

# بررسی logs
docker-compose logs -f
```

## 📁 ساختار پروژه

```
docuchat/
├── backend/              # FastAPI بک‌اند
│   ├── app/
│   │   └── main.py      # مسیرهای API
│   └── tests/
├── frontend/            # Next.js فرانت‌اند
│   ├── src/
│   │   ├── pages/      # صفحات
│   │   ├── components/ # کامپوننت‌ها
│   │   └── hooks/      # Hooks
│   └── stories/        # Storybook
└── infra/              # Terraform & Helm
```

## 🎯 مسیرهای API

### بک‌اند (http://localhost:8000)

- `GET /healthz` - بررسی سلامت
- `POST /v1/chat/demo` - چت دمو
- `GET /docs` - مستندات Swagger

### فرانت‌اند (http://localhost:3000)

- `/` - صفحه خانه
- `/chat` - صفحه چت

## 🔍 حل مشکلات رایج

### خطای اتصال به بک‌اند

**علامت**: "Failed to fetch" یا "Network Error"

**راه‌حل**:
1. بررسی کنید بک‌اند در حال اجراست:
   ```bash
   curl http://localhost:8000/healthz
   ```
2. بررسی `NEXT_PUBLIC_API_BASE` در `.env.local`

### خطای نصب وابستگی‌ها

**Frontend**:
```bash
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

**Backend**:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### خطای Build

**Frontend**:
```bash
rm -rf .next
pnpm build
```

## 📖 مستندات بیشتر

- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)
- [Frontend Implementation](frontend/IMPLEMENTATION.md)
- [Frontend Quickstart](frontend/QUICKSTART.md)

## 🎓 مثال‌های استفاده

### ارسال پیام از cURL

```bash
curl -X POST http://localhost:8000/v1/chat/demo \
  -H "Content-Type: application/json" \
  -d '{"message": "سلام، چطوری؟"}'
```

### تست از JavaScript

```javascript
const response = await fetch('http://localhost:8000/v1/chat/demo', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'سلام' })
});
const data = await response.json();
console.log(data.response);
```

## 🚦 وضعیت پروژه

- ✅ **بک‌اند**: آماده (FastAPI)
- ✅ **فرانت‌اند**: کامل (Next.js + RTL)
- ⏳ **WebSocket**: در انتظار پیاده‌سازی
- ⏳ **احراز هویت**: در انتظار پیاده‌سازی
- ⏳ **بارگذاری PDF**: در انتظار پیاده‌سازی

## 🤝 مشارکت

برای گزارش باگ یا درخواست ویژگی جدید، لطفاً یک issue باز کنید.

## 📞 پشتیبانی

اگر مشکلی دارید:
1. مستندات را مطالعه کنید
2. بررسی کنید که تمام سرویس‌ها در حال اجرا هستند
3. logs را بررسی کنید

---

**آخرین به‌روزرسانی**: 2025-10-06  
**نسخه**: 0.1.0
