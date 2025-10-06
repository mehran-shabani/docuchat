# DocuChat Frontend

فرانت‌اند Next.js با UI چت فارسی راست‌به‌چپ برای DocuChat

## ویژگی‌ها

✅ **RTL کامل**: پشتیبانی کامل از راست‌به‌چپ با فونت فارسی IRANSansX  
✅ **فقط OpenAI**: محدود به مدل‌های رسمی OpenAI (gpt-3.5-turbo, gpt-4o, gpt-4o-mini)  
✅ **دو حالت ارتباط**: HTTP (پیش‌فرض) و WebSocket (با feature flag)  
✅ **Responsive**: طراحی واکنش‌گرا برای موبایل، تبلت و دسکتاپ  
✅ **تست شده**: ≥10 تست واحد با Vitest  
✅ **Storybook**: کامپوننت‌های مستند شده  

## نصب و راه‌اندازی

### پیش‌نیازها

- Node.js 18+
- pnpm (یا npm/yarn)
- بک‌اند DocuChat در حال اجرا روی `http://localhost:8000`

### نصب وابستگی‌ها

```bash
pnpm install
```

### تنظیمات محیط

فایل `.env.local` را از `.env.local.example` کپی کنید:

```bash
cp .env.local.example .env.local
```

سپس مقادیر را بر اساس نیاز تنظیم کنید:

```env
NEXT_PUBLIC_API_BASE=http://localhost:8000
NEXT_PUBLIC_ENABLE_WS=false
NEXT_PUBLIC_WS_ENDPOINT=ws://localhost:8000/ws/chat
NEXT_PUBLIC_OPENAI_MODEL=gpt-3.5-turbo
NEXT_PUBLIC_MODEL_OPTIONS=gpt-3.5-turbo,gpt-4o,gpt-4o-mini
ENABLE_PDF_UPLOAD=true
ENABLE_TEAM_SHARING=false
```

### اجرای Development Server

```bash
pnpm dev
```

سپس به `http://localhost:3000` بروید.

### اجرای تست‌ها

```bash
# اجرای تمام تست‌ها
pnpm test

# اجرای تست‌ها در حالت watch
pnpm test:watch
```

### اجرای Storybook

```bash
pnpm story
```

سپس به `http://localhost:6006` بروید.

### Build برای Production

```bash
pnpm build
pnpm start
```

## ساختار پروژه

```text
frontend/
├── src/
│   ├── pages/              # صفحات Next.js
│   │   ├── _app.tsx        # App wrapper
│   │   ├── index.tsx       # صفحه آغازین
│   │   └── chat.tsx        # صفحه چت
│   ├── components/         # کامپوننت‌های React
│   │   ├── ChatBox.tsx     # کامپوننت اصلی چت
│   │   ├── MessageBubble.tsx
│   │   ├── ModelPicker.tsx
│   │   └── FeatureToggle.tsx
│   ├── hooks/              # React Hooks
│   │   ├── useHttpChat.ts  # اتصال HTTP
│   │   └── useWsChat.ts    # اتصال WebSocket
│   ├── lib/
│   │   └── i18n.ts         # ترجمه‌های فارسی
│   ├── types/
│   │   └── index.ts        # تعریف Type‌ها
│   ├── styles/
│   │   └── globals.css     # استایل‌های global
│   └── __tests__/          # تست‌های واحد
├── stories/                # Storybook stories
├── public/
│   └── fonts/              # فونت‌های فارسی
└── package.json
```

## مدل‌های مجاز

این پروژه **فقط** از مدل‌های OpenAI استفاده می‌کند:

- `gpt-3.5-turbo` (پیش‌فرض)
- `gpt-4o`
- `gpt-4o-mini`

## ویژگی‌های UI

### RTL و فارسی

- جهت راست‌به‌چپ برای تمام متن‌ها
- فونت IRANSansX (با fallback به Vazirmatn از CDN)
- نمایش تاریخ و ساعت به فارسی
- مدیریت صحیح اعداد فارسی/لاتین

### حالت‌های ارتباط

**HTTP (پیش‌فرض):**

- ارسال پیام به `/v1/chat/demo`
- دریافت پاسخ کامل

**WebSocket (اختیاری):**

- فعال با `NEXT_PUBLIC_ENABLE_WS=true`
- استریم token-by-token از `/ws/chat`
- Fallback خودکار به HTTP در صورت خطا

### Responsive Design

- موبایل: 375px+
- تبلت: 768px+
- دسکتاپ: 1024px+
- عرض کامل: 1440px+

## تست‌ها

پوشش تست‌ها شامل:

1. ✅ رندر صحیح MessageBubble در RTL
2. ✅ نمایش پیام‌های user و assistant
3. ✅ نشانگر استریم در حالت streaming
4. ✅ انتخاب مدل از ModelPicker
5. ✅ فیلتر کردن مدل‌های غیرمجاز
6. ✅ نمایش وضعیت Feature Flags
7. ✅ ارسال پیام با useHttpChat
8. ✅ مدیریت خطا در HTTP
9. ✅ پاک کردن پیام‌ها
10. ✅ اعتبارسنجی ورودی (عدم ارسال پیام خالی)

## مشارکت

برای گزارش باگ یا درخواست ویژگی جدید، لطفاً یک issue باز کنید.

## لایسنس

MIT
