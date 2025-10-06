import type { Meta, StoryObj } from '@storybook/react';
import { ChatBox } from '../src/components/ChatBox';

const meta: Meta<typeof ChatBox> = {
  title: 'Components/ChatBox',
  component: ChatBox,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
  },
};

export default meta;
type Story = StoryObj<typeof ChatBox>;

export const Default: Story = {};

export const RTLView: Story = {
  decorators: [
    (Story) => (
      <div dir="rtl">
        <Story />
      </div>
    ),
  ],
};

export const MobileView: Story = {
  parameters: {
    viewport: {
      defaultViewport: 'mobile1',
    },
  },
};

export const TabletView: Story = {
  parameters: {
    viewport: {
      defaultViewport: 'tablet',
    },
  },
};
