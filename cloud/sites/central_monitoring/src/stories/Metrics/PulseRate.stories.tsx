import PulseRate from '@/app/(authenticated)/home/details/Metrics/PulseRate';
import { ERROR_VALUE } from '@/constants';
import { Meta, StoryObj } from '@storybook/react';

const meta: Meta<typeof PulseRate> = {
  component: PulseRate,
  title: 'Metrics/PulseRate',
  argTypes: {
    timestamp: { control: 'date' },
  },
  args: {
    isConnected: true,
    isLoading: false,
    measurement: {
      value: 100,
      upperLimit: '120',
      lowerLimit: '45',
    },
    unit: 'bpm',
    timestamp: Date.now().toString(),
  },
};

export default meta;
type Story = StoryObj<typeof PulseRate>;

export const Loading: Story = {
  args: {
    isLoading: true,
  },
};

export const Error: Story = {
  args: {
    measurement: {
      value: ERROR_VALUE,
    },
  },
};
export const Disconnected: Story = {
  args: {
    isConnected: false,
  },
};

export const Default: Story = {};

export const TwoHoursAgo: Story = {
  args: {
    timestamp: (Date.now() - 2 * 3600000).toString(),
  },
};
