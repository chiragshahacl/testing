import FallDetector from '@/app/(authenticated)/home/details/Metrics/FallDetector';
import { FallState } from '@/types/metrics';
import { ALERT_PRIORITY } from '@/utils/metricCodes';
import { Meta, StoryObj } from '@storybook/react';

const meta: Meta<typeof FallDetector> = {
  component: FallDetector,
  title: 'Metrics/FallDetector',
  args: {
    state: FallState.DETECTED,
  },
};

export default meta;
type Story = StoryObj<typeof FallDetector>;

export const Detected: Story = {};

export const NotDetected: Story = {
  args: {
    state: FallState.NOT_DETECTED,
  },
};

export const HighPriority: Story = {
  args: {
    alertPriority: ALERT_PRIORITY.HIGH,
  },
};

export const MediumPriority: Story = {
  args: {
    alertPriority: ALERT_PRIORITY.MEDIUM,
  },
};
export const LowPriority: Story = {
  args: {
    alertPriority: ALERT_PRIORITY.LOW,
  },
};

export const InternalPriority: Story = {
  args: {
    alertPriority: ALERT_PRIORITY.INTERNAL,
  },
};

export const NoPriority: Story = {
  args: {
    alertPriority: undefined,
  },
};

export const Loading: Story = {
  args: {
    isLoading: true,
  },
};

export const NoState: Story = {
  args: {
    state: null,
  },
};
