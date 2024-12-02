import Oximeter from '@/app/(authenticated)/home/details/Metrics/Oximeter';
import { ALERT_PRIORITY } from '@/utils/metricCodes';
import { expect } from '@storybook/jest';
import { Meta, StoryObj } from '@storybook/react';
import { waitFor, within } from '@storybook/testing-library';

const meta: Meta<typeof Oximeter> = {
  component: Oximeter,
  title: 'Metrics/Oximeter',
  args: {
    isConnected: true,
    isError: false,
    isLoading: false,
    value: 100,
    unit: '%',
    threshold: {
      upperLimit: '120',
      lowerLimit: '45',
    },
  },
  play: async ({ canvasElement, args: { value, threshold, alertPriority } }) => {
    if (
      alertPriority &&
      [
        ALERT_PRIORITY.HIGH,
        ALERT_PRIORITY.MEDIUM,
        ALERT_PRIORITY.LOW,
        ALERT_PRIORITY.INTERNAL,
      ].includes(alertPriority)
    ) {
      const canvas = within(canvasElement);
      await waitFor(() => {
        if (value) {
          const rate = canvas.getByText(value);
          expect(rate).toHaveStyle('color: #000000');
        }
        if (threshold) {
          const upperValue = canvas.getByText(threshold.upperLimit);
          const lowerValue = canvas.getByText(threshold.lowerLimit);
          expect(upperValue).toHaveStyle('color: #000000');
          expect(lowerValue).toHaveStyle('color: #000000');
        }
      });
    }
  },
};

export default meta;
type Story = StoryObj<typeof Oximeter>;

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
