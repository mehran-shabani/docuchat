import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FeatureToggle } from '@/components/FeatureToggle';

describe('FeatureToggle', () => {
  it('renders settings title', () => {
    render(<FeatureToggle />);
    expect(screen.getByText('تنظیمات')).toBeInTheDocument();
  });

  it('displays WebSocket status', () => {
    render(<FeatureToggle />);
    // Default is disabled
    expect(screen.getByText(/استریم/)).toBeInTheDocument();
  });

  it('displays PDF upload status', () => {
    render(<FeatureToggle />);
    expect(screen.getByText(/آپلود PDF/)).toBeInTheDocument();
  });

  it('applies RTL direction', () => {
    const { container } = render(<FeatureToggle />);
    const toggleContainer = container.querySelector('[dir="rtl"]');
    expect(toggleContainer).toBeInTheDocument();
  });
});
