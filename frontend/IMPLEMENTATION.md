# پیاده‌سازی فرانت‌اند DocuChat

## ✅ وضعیت پیاده‌سازی

تمام الزامات پرامپت ۲ با موفقیت پیاده‌سازی شد.

### معماری کلی

```
Frontend (Next.js 14 + React 18 + Tailwind)
    ↓
HTTP /v1/chat/demo (پیش‌فرض)
WebSocket /ws/chat (با feature flag)
    ↓
Backend (FastAPI - از پرامپت ۱)
```

## 📁 ساختار پروژه

```
frontend/
├── src/
│   ├── pages/                   # صفحات Next.js
│   │   ├── _app.tsx            # کانفیگ اپلیکیشن
│   │   ├── index.tsx           # صفحه خانه (welcoming)
│   │   └── chat.tsx            # صفحه چت اصلی
│   ├── components/              # کامپوننت‌های React
│   │   ├── ChatBox.tsx         # کامپوننت اصلی چت
│   │   ├── MessageBubble.tsx   # نمایش پیام‌ها
│   │   ├── ModelPicker.tsx     # انتخاب مدل OpenAI
│   │   └── FeatureToggle.tsx   # نمایش Feature Flags
│   ├── hooks/                   # React Hooks
│   │   ├── useHttpChat.ts      # هوک ارتباط HTTP
│   │   └── useWsChat.ts        # هوک ارتباط WebSocket
│   ├── lib/
│   │   └── i18n.ts             # ترجمه‌های فارسی
│   ├── types/
│   │   └── index.ts            # تعاریف TypeScript
│   ├── styles/
│   │   └── globals.css         # استایل‌های global + RTL
│   ├── __tests__/               # تست‌های واحد (23 تست)
│   └── test/
│       └── setup.ts            # کانفیگ Vitest
├── stories/                     # Storybook stories (4 stories)
├── public/
│   └── fonts/                  # فونت‌های فارسی
├── .storybook/                 # کانفیگ Storybook
├── package.json                # وابستگی‌ها و اسکریپت‌ها
├── next.config.js              # کانفیگ Next.js
├── tailwind.config.js          # کانفیگ Tailwind + RTL
├── tsconfig.json               # کانفیگ TypeScript
├── vitest.config.ts            # کانفیگ Vitest
└── .env.local.example          # نمونه تنظیمات محیطی
```

## 🎯 پذیرش (Acceptance Criteria)

### ✅ 1. اتصال HTTP (پیش‌فرض)

- [x] `useHttpChat` hook برای ارتباط با `/v1/chat/demo`
- [x] ارسال `POST` با body: `{ message, model }`
- [x] دریافت پاسخ کامل از بک‌اند
- [x] نمایش پیام‌ها در `ChatBox`
- [x] مدیریت خطا و نمایش پیام خطا

### ✅ 2. اتصال WebSocket (اختیاری)

- [x] `useWsChat` hook برای ارتباط استریم
- [x] اتصال به `/ws/chat` با `NEXT_PUBLIC_ENABLE_WS=true`
- [x] دریافت توکن‌های استریم (token-by-token)
- [x] نمایش لحظه‌ای پیام‌ها
- [x] Fallback خودکار به HTTP در صورت خطا
- [x] Reconnect خودکار پس از قطع اتصال

### ✅ 3. محدودیت به OpenAI

- [x] فقط مدل‌های OpenAI: `gpt-3.5-turbo`, `gpt-4o`, `gpt-4o-mini`
- [x] `ALLOWED_OPENAI_MODELS` در `types/index.ts`
- [x] `ModelPicker` فیلتر کردن مدل‌های غیرمجاز
- [x] پارس کردن `NEXT_PUBLIC_MODEL_OPTIONS` از ENV
- [x] هیچ اشاره‌ای به مدل‌های غیر OpenAI

### ✅ 4. RTL و فارسی

- [x] فونت IRANSansX (با fallback CDN)
- [x] جهت `dir="rtl"` در `<html>`
- [x] `tailwindcss-rtl` پلاگین
- [x] ترجمه‌های فارسی در `lib/i18n.ts`
- [x] نمایش تاریخ به فارسی
- [x] scrollbar سفارشی برای RTL

### ✅ 5. صفحات

- [x] `index.tsx`: صفحه خوش‌آمدگویی با لینک به چت
- [x] `chat.tsx`: صفحه چت کامل
- [x] `_app.tsx`: کانفیگ global با Head

### ✅ 6. کامپوننت‌ها

- [x] `ChatBox`: کامپوننت اصلی با sidebar
- [x] `MessageBubble`: نمایش پیام با RTL کامل
- [x] `ModelPicker`: انتخاب مدل از dropdown
- [x] `FeatureToggle`: نمایش Feature Flags

### ✅ 7. تست‌ها (≥10)

- [x] 23 تست واحد با Vitest
- [x] Coverage برای components, hooks, types, i18n
- [x] تست RTL rendering
- [x] تست HTTP chat flow
- [x] تست model selection
- [x] تست error handling
- [x] همه تست‌ها PASS ✓

### ✅ 8. Storybook

- [x] 4 Story برای کامپوننت‌های اصلی
- [x] کنترل RTL در Storybook
- [x] Stories برای حالت‌های مختلف (user/assistant/streaming)
- [x] کانفیگ کامل `.storybook/`

### ✅ 9. Responsive Design

- [x] موبایل: 375px+ (tested)
- [x] تبلت: 768px+
- [x] دسکتاپ: 1024px+
- [x] Large desktop: 1440px+

### ✅ 10. Build و Scripts

- [x] `pnpm dev` → Development server
- [x] `pnpm build` → Production build ✓
- [x] `pnpm test` → Run tests ✓
- [x] `pnpm story` → Storybook dev

## 🔧 متغیرهای محیطی

```env
# API Backend
NEXT_PUBLIC_API_BASE=http://localhost:8000

# WebSocket (اختیاری)
NEXT_PUBLIC_ENABLE_WS=false
NEXT_PUBLIC_WS_ENDPOINT=ws://localhost:8000/ws/chat

# مدل OpenAI
NEXT_PUBLIC_OPENAI_MODEL=gpt-3.5-turbo
NEXT_PUBLIC_MODEL_OPTIONS=gpt-3.5-turbo,gpt-4o,gpt-4o-mini

# Feature Flags
ENABLE_PDF_UPLOAD=true          # برای ایجنت ۳
ENABLE_TEAM_SHARING=false       # برای آینده
```

## 📊 نتایج تست

```
Test Files: 6 passed (6)
Tests: 23 passed (23)
Duration: ~3.67s
```

**تست‌های اصلی:**
1. رندر MessageBubble در RTL
2. نمایش user/assistant messages
3. نشانگر streaming
4. ModelPicker با فیلتر OpenAI
5. FeatureToggle status
6. HTTP chat flow
7. Error handling
8. Clear messages
9. Empty message validation
10. i18n translations
11. Type validation
... و 12 تست دیگر

## 🎨 ویژگی‌های UI

### طراحی
- Gradient background (blue to indigo)
- Shadow و rounded corners مدرن
- رنگ‌بندی: Indigo (primary), White/Gray (backgrounds)
- انیمیشن‌های smooth (hover, pulse)

### تجربه کاربری
- Placeholder فارسی
- لودینگ state با متن فارسی
- پیام‌های خطا با RTL
- Auto-scroll به آخرین پیام
- Shift+Enter برای خط جدید
- Disable button در حالت loading

### Accessibility
- Semantic HTML
- ARIA labels
- Keyboard navigation
- Focus states

## 🚀 راه‌اندازی سریع

```bash
cd frontend
pnpm install
cp .env.local.example .env.local
pnpm dev
```

سپس به `http://localhost:3000` بروید.

## 📝 نکات برای ایجنت بعدی (بک‌اند)

### الزامات برای ایجنت ۳ (بک‌اند):

1. **مسیرهای موجود:**
   - `GET /healthz` ✓
   - `POST /v1/chat/demo` ✓

2. **مسیرهای مورد نیاز:**
   - `WebSocket /ws/chat` برای استریم
   - احراز هویت (email + code)
   - بارگذاری PDF
   - RAG با OpenAI Embeddings

3. **استفاده از OpenAI:**
   - فقط `openai` کتابخانه رسمی
   - Chat Completions API
   - Embeddings API (text-embedding-3-small)
   - استریم response

4. **تطابق با Frontend:**
   - Request format: `{ message: string, model?: string }`
   - Response format: `{ response: string }`
   - WebSocket messages: `{ type: 'token' | 'end' | 'error', content?: string }`

## 🏆 خلاصه

✅ **تمام الزامات پرامپت ۲ پیاده‌سازی شد:**

- فرانت‌اند Next.js 14 کامل با RTL فارسی
- فقط از مدل‌های OpenAI استفاده می‌شود
- دو حالت HTTP و WebSocket
- 23 تست واحد (همه PASS)
- 4 Storybook stories
- Build موفق
- Responsive design
- مستندات کامل

**آماده برای ایجنت ۳** که باید بک‌اند را کامل کند! 🎉
