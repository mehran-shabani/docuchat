import type { Meta, StoryObj } from '@storybook/react';
import { MessageBubble } from '../src/components/MessageBubble';

const meta: Meta<typeof MessageBubble> = {
  title: 'Components/MessageBubble',
  component: MessageBubble,
  tags: ['autodocs'],
  parameters: {
    layout: 'padded',
  },
};

export default meta;
type Story = StoryObj<typeof MessageBubble>;

export const UserMessage: Story = {
  args: {
    message: {
      id: '1',
      role: 'user',
      content: 'سلام! این یک پیام نمونه از کاربر است.',
      timestamp: new Date().toISOString(),
    },
  },
};

export const AssistantMessage: Story = {
  args: {
    message: {
      id: '2',
      role: 'assistant',
      content: 'سلام! من دستیار هوشمند هستم. چطور می‌توانم به شما کمک کنم؟',
      timestamp: new Date().toISOString(),
    },
  },
};

export const StreamingMessage: Story = {
  args: {
    message: {
      id: '3',
      role: 'assistant',
      content: 'در حال تایپ پاسخ...',
      timestamp: new Date().toISOString(),
      streaming: true,
    },
  },
};

export const LongMessage: Story = {
  args: {
    message: {
      id: '4',
      role: 'assistant',
      content: `این یک پیام طولانی است که نشان می‌دهد چگونه پیام‌های طولانی در رابط کاربری نمایش داده می‌شوند.

در اینجا چند نکته مهم:
• استفاده از فونت فارسی IRANSansX
• پشتیبانی کامل از RTL
• نمایش زمان به صورت فارسی
• مدیریت خطوط جدید و فاصله‌ها

این متن برای تست نمایش محتوای طولانی طراحی شده است.`,
      timestamp: new Date().toISOString(),
    },
  },
};
