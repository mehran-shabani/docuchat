import type { Preview } from '@storybook/react';
import React from 'react';
import '../src/styles/globals.css';

const preview: Preview = {
  parameters: {
    actions: { argTypesRegex: '^on[A-Z].*' },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/,
      },
    },
  },
  globalTypes: {
    direction: {
      name: 'Direction',
      description: 'Text direction',
      defaultValue: 'rtl',
      toolbar: {
        icon: 'paragraph',
        items: ['ltr', 'rtl'],
        showName: true,
      },
    },
  },
  decorators: [
    (Story, context) => (
      <div dir={context.globals.direction}>
        <Story />
      </div>
    ),
  ],
};

export default preview;
