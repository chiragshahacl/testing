import PerfusionIndex from '@/app/(authenticated)/home/details/Metrics/PerfusionIndex';
import { Meta, StoryObj } from '@storybook/react';

const meta: Meta<typeof PerfusionIndex> = {
  component: PerfusionIndex,
  title: 'Metrics/PerfusionIndex',
  args: {
    isConnected: true,
    isError: false,
    isLoading: false,
    value: 100,
    unit: '%',
  },
};

export default meta;
type Story = StoryObj<typeof PerfusionIndex>;

export const Loading: Story = {
  args: {
    isLoading: true,
  },
};

export const Error: Story = {
  args: {
    isError: true,
  },
};

export const Disconnected: Story = {
  args: {
    isConnected: false,
  },
};
export const Default: Story = {};

export const NoValue: Story = {
  args: {
    value: undefined,
  },
};
