# فایل‌های ایجاد شده برای فرانت‌اند DocuChat

## ساختار کامل

### پوشه اصلی frontend/
```
frontend/
├── .env.local.example          # نمونه تنظیمات محیطی
├── .gitignore                  # فایل‌های ignore شده
├── package.json                # وابستگی‌ها (25 package)
├── next.config.js              # کانفیگ Next.js
├── tailwind.config.js          # کانفیگ Tailwind + RTL
├── tsconfig.json               # کانفیگ TypeScript
├── vitest.config.ts            # کانفیگ Vitest
├── postcss.config.js           # کانفیگ PostCSS (موجود)
├── README.md                   # مستندات اصلی
├── IMPLEMENTATION.md           # جزئیات پیاده‌سازی
└── QUICKSTART.md               # راهنمای سریع
```

### کانفیگ Storybook
```
.storybook/
├── main.ts                     # کانفیگ اصلی Storybook
└── preview.ts                  # تنظیمات نمایش + RTL
```

### کد منبع
```
src/
├── pages/
│   ├── _app.tsx               # App wrapper با Head
│   ├── index.tsx              # صفحه خانه
│   └── chat.tsx               # صفحه چت
│
├── components/
│   ├── ChatBox.tsx            # کامپوننت اصلی چت
│   ├── MessageBubble.tsx      # نمایش پیام‌ها
│   ├── ModelPicker.tsx        # انتخاب مدل OpenAI
│   └── FeatureToggle.tsx      # نمایش feature flags
│
├── hooks/
│   ├── useHttpChat.ts         # هوک HTTP chat
│   └── useWsChat.ts           # هوک WebSocket chat
│
├── lib/
│   └── i18n.ts                # ترجمه‌های فارسی
│
├── types/
│   └── index.ts               # تعاریف TypeScript
│
├── styles/
│   └── globals.css            # استایل‌های global + RTL
│
├── test/
│   └── setup.ts               # کانفیگ تست
│
└── __tests__/
    ├── MessageBubble.test.tsx
    ├── ModelPicker.test.tsx
    ├── FeatureToggle.test.tsx
    ├── useHttpChat.test.tsx
    ├── i18n.test.ts
    └── types.test.ts
```

### Storybook Stories
```
stories/
├── ChatBox.stories.tsx
├── MessageBubble.stories.tsx
├── ModelPicker.stories.tsx
└── FeatureToggle.stories.tsx
```

### Public Assets
```
public/
└── fonts/
    └── IRANSansX-README.md    # راهنمای فونت
```

## آمار

- **کل فایل‌های جدید**: ~30 فایل
- **خطوط کد**: ~2,000+ LOC
- **تست‌ها**: 23
- **Stories**: 4
- **کامپوننت‌ها**: 4
- **Hooks**: 2
- **صفحات**: 3

## فایل‌های کلیدی

### 1. کانفیگ و Setup
- `package.json` - 25+ وابستگی
- `tailwind.config.js` - RTL + Typography
- `vitest.config.ts` - تست کانفیگ
- `.env.local.example` - 7 متغیر محیطی

### 2. کامپوننت‌های اصلی
- `ChatBox.tsx` - ~200 خط
- `MessageBubble.tsx` - ~50 خط
- `ModelPicker.tsx` - ~70 خط
- `FeatureToggle.tsx` - ~80 خط

### 3. Hooks
- `useHttpChat.ts` - ~80 خط
- `useWsChat.ts` - ~150 خط

### 4. تست‌ها
- 6 فایل تست با 23 test case

### 5. مستندات
- `README.md` - راهنمای کامل
- `IMPLEMENTATION.md` - جزئیات فنی
- `QUICKSTART.md` - شروع سریع

## تکنولوژی‌های استفاده شده

### Core
- Next.js 14.2
- React 18.3
- TypeScript 5.4

### Styling
- Tailwind CSS 3.4
- tailwindcss-rtl 0.9
- @tailwindcss/typography 0.5

### Testing
- Vitest 1.6
- @testing-library/react 14.3
- @testing-library/jest-dom 6.1

### Development
- Storybook 7.6
- ESLint 8.57
- PostCSS 8.4

## ویژگی‌های پیاده‌سازی شده

✅ RTL کامل با فونت فارسی  
✅ دو حالت ارتباط: HTTP + WebSocket  
✅ محدودیت به مدل‌های OpenAI  
✅ Responsive Design (375px - 1440px+)  
✅ تست‌های جامع (23 تست)  
✅ Storybook برای مستندسازی  
✅ مدیریت خطا و fallback  
✅ Feature flags  
✅ TypeScript کامل  
✅ مستندات جامع  

---

**تاریخ**: 2025-10-06  
**وضعیت**: COMPLETE ✓
