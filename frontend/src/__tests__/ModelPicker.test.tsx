import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ModelPicker } from '@/components/ModelPicker';

describe('ModelPicker', () => {
  it('renders model select dropdown', () => {
    const onModelChange = vi.fn();
    render(<ModelPicker onModelChange={onModelChange} />);
    
    expect(screen.getByLabelText(/مدل/)).toBeInTheDocument();
  });

  it('displays only OpenAI models', () => {
    const onModelChange = vi.fn();
    render(<ModelPicker onModelChange={onModelChange} />);
    
    const select = screen.getByRole('combobox');
    const options = select.querySelectorAll('option');
    
    options.forEach(option => {
      expect(['gpt-3.5-turbo', 'gpt-4o', 'gpt-4o-mini']).toContain(option.value);
    });
  });

  it('calls onModelChange when model is changed', () => {
    const onModelChange = vi.fn();
    render(<ModelPicker onModelChange={onModelChange} currentModel="gpt-3.5-turbo" />);
    
    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: 'gpt-4o' } });
    
    expect(onModelChange).toHaveBeenCalledWith('gpt-4o');
  });

  it('sets default model from props', () => {
    const onModelChange = vi.fn();
    render(<ModelPicker onModelChange={onModelChange} currentModel="gpt-4o-mini" />);
    
    const select = screen.getByRole('combobox') as HTMLSelectElement;
    expect(select.value).toBe('gpt-4o-mini');
  });
});
