import type { Meta, StoryObj } from '@storybook/react';
import { ModelPicker } from '../src/components/ModelPicker';

const meta: Meta<typeof ModelPicker> = {
  title: 'Components/ModelPicker',
  component: ModelPicker,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
};

export default meta;
type Story = StoryObj<typeof ModelPicker>;

export const Default: Story = {
  args: {
    onModelChange: (model) => console.log('Model changed to:', model),
  },
};

export const WithGPT4o: Story = {
  args: {
    currentModel: 'gpt-4o',
    onModelChange: (model) => console.log('Model changed to:', model),
  },
};

export const WithGPT4oMini: Story = {
  args: {
    currentModel: 'gpt-4o-mini',
    onModelChange: (model) => console.log('Model changed to:', model),
  },
};

export const WithGPT35Turbo: Story = {
  args: {
    currentModel: 'gpt-3.5-turbo',
    onModelChange: (model) => console.log('Model changed to:', model),
  },
};
