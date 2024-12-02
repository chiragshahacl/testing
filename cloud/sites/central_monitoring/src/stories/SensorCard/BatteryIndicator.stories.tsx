import { expect } from '@storybook/jest';
import type { Meta, StoryObj } from '@storybook/react';

import BatteryIndicator from '@/components/cards/SensorCard/BatteryIndicator';
import { screen } from '@storybook/testing-library';

const meta: Meta<typeof BatteryIndicator> = {
  component: BatteryIndicator,
  argTypes: { battery: { control: { type: 'range', min: 0, max: 100, step: 1 } } },
  title: 'SensorCard/Battery Indicator',
  play: async ({ args: { battery } }) => {
    expect(screen.getByText(`${battery}%`)).toBeInTheDocument();
  },
};

export default meta;
type Story = StoryObj<typeof BatteryIndicator>;

export const Empty: Story = {
  args: {
    battery: 0,
  },
};

export const Low: Story = {
  args: {
    battery: 20,
  },
};

export const MidLow: Story = {
  args: {
    battery: 40,
  },
};

export const MidHigh: Story = {
  args: {
    battery: 60,
  },
};

export const High: Story = {
  args: {
    battery: 80,
  },
};

export const Full: Story = {
  args: {
    battery: 100,
  },
};
