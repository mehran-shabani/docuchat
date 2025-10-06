import { describe, it, expect } from 'vitest';
import { t, faTranslations } from '@/lib/i18n';

describe('i18n', () => {
  it('returns correct translation for valid key', () => {
    expect(t('welcome')).toBe('به DocuChat خوش آمدید');
    expect(t('send')).toBe('ارسال');
    expect(t('placeholder')).toBe('پیام خود را بنویسید...');
  });

  it('has all required translation keys', () => {
    const requiredKeys = [
      'welcome',
      'send',
      'placeholder',
      'model',
      'settings',
      'startChat',
      'error',
      'retry',
    ];

    requiredKeys.forEach(key => {
      expect(faTranslations).toHaveProperty(key);
    });
  });

  it('all translations are non-empty strings', () => {
    Object.values(faTranslations).forEach(value => {
      expect(typeof value).toBe('string');
      expect(value.length).toBeGreaterThan(0);
    });
  });
});
