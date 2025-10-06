# 🚀 راه‌اندازی سریع فرانت‌اند DocuChat

## نصب

```bash
cd frontend
pnpm install
```

## تنظیمات

```bash
cp .env.local.example .env.local
```

تنظیمات پیشنهادی برای توسعه:

```env
NEXT_PUBLIC_API_BASE=http://localhost:8000
NEXT_PUBLIC_ENABLE_WS=false
NEXT_PUBLIC_OPENAI_MODEL=gpt-3.5-turbo
NEXT_PUBLIC_MODEL_OPTIONS=gpt-3.5-turbo,gpt-4o,gpt-4o-mini
```

## اجرا

### Development Server

```bash
pnpm dev
```

باز کردن: `http://localhost:3000`

### تست‌ها

```bash
# تست یک‌بار
pnpm test

# تست در حالت watch
pnpm test:watch
```

### Storybook

```bash
pnpm story
```

باز کردن: `http://localhost:6006`

### Production Build

```bash
pnpm build
pnpm start
```

## ساختار صفحات

- `/` - صفحه خوش‌آمدگویی
- `/chat` - صفحه چت اصلی

## مدل‌های مجاز

✅ `gpt-3.5-turbo`  
✅ `gpt-4o`  
✅ `gpt-4o-mini`  

❌ سایر مدل‌ها (غیر OpenAI)

## Feature Flags

### WebSocket Streaming
```env
NEXT_PUBLIC_ENABLE_WS=true
NEXT_PUBLIC_WS_ENDPOINT=ws://localhost:8000/ws/chat
```

### آپلود PDF (برای آینده)
```env
ENABLE_PDF_UPLOAD=true
```

## نکات مهم

1. **بک‌اند باید روی `http://localhost:8000` اجرا شود**
2. **فقط از مدل‌های OpenAI استفاده شود**
3. **جهت RTL به صورت خودکار اعمال می‌شود**
4. **WebSocket به صورت پیش‌فرض غیرفعال است**

## کلیدهای میانبر

- `Enter` - ارسال پیام
- `Shift + Enter` - خط جدید

## حل مشکلات

### خطای اتصال به بک‌اند

بررسی کنید که بک‌اند روی `http://localhost:8000` در حال اجراست:

```bash
curl http://localhost:8000/healthz
```

### خطای WebSocket

WebSocket را غیرفعال کنید:

```env
NEXT_PUBLIC_ENABLE_WS=false
```

### خطای Build

پاک کردن cache:

```bash
rm -rf .next
pnpm build
```

## مستندات بیشتر

- [README.md](./README.md) - مستندات کامل
- [IMPLEMENTATION.md](./IMPLEMENTATION.md) - جزئیات پیاده‌سازی
