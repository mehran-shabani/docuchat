export const faTranslations = {
  welcome: 'به DocuChat خوش آمدید',
  send: 'ارسال',
  placeholder: 'پیام خود را بنویسید...',
  model: 'مدل',
  settings: 'تنظیمات',
  startChat: 'شروع گفتگو',
  error: 'خطا',
  retry: 'تلاش مجدد',
  
  // General UI
  connected: 'متصل',
  ready: 'برای شروع آماده‌اید؟',
  description: 'با دستیار هوشمند گفتگو کنید و پاسخ سریع بگیرید.',
  version: 'نسخه',
  backendActive: 'پشتیبان فعال است',
  openaiOnly: 'فقط مدل‌های OpenAI',
  rtlPersian: 'نمایش راست‌به‌چپ فارسی',
  loading: 'در حال ارسال...',

  // Chat roles and statuses
  user: 'شما',
  assistant: 'دستیار',
  typing: 'در حال تایپ...',

  // Feature toggles
  wsEnabled: 'استریم وب‌سوکت فعال است',
  wsDisabled: 'استریم وب‌سوکت غیرفعال است',
  pdfUploadEnabled: 'آپلود PDF فعال است',
  pdfUploadDisabled: 'آپلود PDF غیرفعال است',
} as const;

export type TranslationKey = keyof typeof faTranslations;

export function t(key: TranslationKey | string): string {
  const dict = faTranslations as Record<string, string>;
  return dict[key] ?? key;
}
