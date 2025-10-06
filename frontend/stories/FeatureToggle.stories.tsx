import type { Meta, StoryObj } from '@storybook/react';
import { FeatureToggle } from '../src/components/FeatureToggle';

const meta: Meta<typeof FeatureToggle> = {
  title: 'Components/FeatureToggle',
  component: FeatureToggle,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
};

export default meta;
type Story = StoryObj<typeof FeatureToggle>;

export const Default: Story = {
  args: {
    onFlagsChange: (flags) => console.log('Flags changed:', flags),
  },
};

export const RTLView: Story = {
  args: {
    onFlagsChange: (flags) => console.log('Flags changed:', flags),
  },
  decorators: [
    (Story) => (
      <div dir="rtl" style={{ minWidth: '300px' }}>
        <Story />
      </div>
    ),
  ],
};
