import BodyPosition from '@/app/(authenticated)/home/details/Metrics/BodyPosition';
import { ALERT_PRIORITY, POSITION_TYPES } from '@/utils/metricCodes';
import { Meta, StoryObj } from '@storybook/react';

const meta: Meta<typeof BodyPosition> = {
  component: BodyPosition,
  title: 'Metrics/BodyPosition',
  args: {
    isConnected: true,
    hoursInCurrentPosition: '04',
    minutesInCurrentPosition: '20',
    position: POSITION_TYPES.UPRIGHT,
    angle: '40',
  },
};

export default meta;
type Story = StoryObj<typeof BodyPosition>;

export const ValidValue: Story = {
  args: {},
};

export const InvalidBodyPosition: Story = {
  args: {
    position: null,
    angle: NaN,
  },
};

export const Loading: Story = {
  args: {
    isLoading: true,
  },
};

export const Disconnected: Story = {
  args: {
    isConnected: false,
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

export const HasTechnicalAlerts: Story = {
  args: {
    hasTechnicalAlert: true,
  },
};
