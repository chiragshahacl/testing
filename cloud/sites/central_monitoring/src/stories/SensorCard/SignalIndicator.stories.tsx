import SignalIndicator from '@/components/cards/SensorCard/SignalIndicator';
import type { Meta, StoryObj } from '@storybook/react';

const meta: Meta<typeof SignalIndicator> = {
  component: SignalIndicator,
  argTypes: { signal: { control: { type: 'range', min: -100, max: 0, step: 1 } } },
  title: 'SensorCard/Signal Indicator',
};

export default meta;
type Story = StoryObj<typeof SignalIndicator>;

export const Low: Story = {
  args: {
    signal: -100,
  },
};
