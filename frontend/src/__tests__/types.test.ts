import { describe, it, expect } from 'vitest';
import { ALLOWED_OPENAI_MODELS } from '@/types';

describe('Types', () => {
  it('ALLOWED_OPENAI_MODELS contains only valid OpenAI models', () => {
    const validModels = ['gpt-3.5-turbo', 'gpt-4o', 'gpt-4o-mini'];
    
    ALLOWED_OPENAI_MODELS.forEach(model => {
      expect(validModels).toContain(model);
    });
  });

  it('ALLOWED_OPENAI_MODELS is not empty', () => {
    expect(ALLOWED_OPENAI_MODELS.length).toBeGreaterThan(0);
  });

  it('ALLOWED_OPENAI_MODELS contains gpt-3.5-turbo as default', () => {
    expect(ALLOWED_OPENAI_MODELS).toContain('gpt-3.5-turbo');
  });
});
