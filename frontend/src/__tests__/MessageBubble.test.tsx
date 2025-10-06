import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MessageBubble } from '@/components/MessageBubble';
import type { Message } from '@/types';

describe('MessageBubble', () => {
  it('renders user message correctly', () => {
    const message: Message = {
      id: '1',
      role: 'user',
      content: 'سلام',
      timestamp: new Date(),
    };

    render(<MessageBubble message={message} />);
    expect(screen.getByText('سلام')).toBeInTheDocument();
    expect(screen.getByText('شما')).toBeInTheDocument();
  });

  it('renders assistant message correctly', () => {
    const message: Message = {
      id: '2',
      role: 'assistant',
      content: 'سلام! چطور می‌توانم کمکتان کنم؟',
      timestamp: new Date(),
    };

    render(<MessageBubble message={message} />);
    expect(screen.getByText(/سلام! چطور می‌توانم کمکتان کنم؟/)).toBeInTheDocument();
    expect(screen.getByText('دستیار')).toBeInTheDocument();
  });

  it('shows streaming indicator when message is streaming', () => {
    const message: Message = {
      id: '3',
      role: 'assistant',
      content: 'در حال پاسخ...',
      timestamp: new Date(),
      streaming: true,
    };

    render(<MessageBubble message={message} />);
    expect(screen.getByText('در حال تایپ...')).toBeInTheDocument();
  });

  it('applies correct RTL direction', () => {
    const message: Message = {
      id: '4',
      role: 'user',
      content: 'تست RTL',
      timestamp: new Date(),
    };

    const { container } = render(<MessageBubble message={message} />);
    const messageContainer = container.querySelector('[dir="rtl"]');
    expect(messageContainer).toBeInTheDocument();
  });
});
