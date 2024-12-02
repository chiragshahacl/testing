import LimbTemperature from '@/app/(authenticated)/home/details/Metrics/LimbTemperature';
import { ALERT_PRIORITY } from '@/utils/metricCodes';
import { expect } from '@storybook/jest';
import { Meta, StoryObj } from '@storybook/react';
import { waitFor, within } from '@storybook/testing-library';

const meta: Meta<typeof LimbTemperature> = {
  component: LimbTemperature,
  title: 'Metrics/LimbTemperature',
  args: {
    isConnected: true,
    isLoading: false,
    measurement: {
      value: 98.6,
      upperLimit: '100',
      lowerLimit: '90',
    },
  },
  play: async ({ canvasElement, args: { measurement, alertPriority } }) => {
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
        if (measurement.value) {
          const value = canvas.getByText(measurement.value);
          expect(value).toHaveStyle('color: #000000');
        }
        if (measurement.upperLimit) {
          const upperValue = canvas.getByText(measurement.upperLimit);
          expect(upperValue).toHaveStyle('color: #000000');
        }
        if (measurement.lowerLimit) {
          const lowerValue = canvas.getByText(measurement.lowerLimit);
          expect(lowerValue).toHaveStyle('color: #000000');
        }
      });
    }
  },
};

export default meta;
type Story = StoryObj<typeof LimbTemperature>;

export const LoadingNoBounds: Story = {
  args: {
    isLoading: true,
    measurement: {
      value: 98.6,
    },
  },
};

export const LoadingBounded: Story = {
  args: {
    isLoading: true,
  },
};

export const Disconnect: Story = {
  args: {
    isConnected: false,
  },
};

export const HighPriority: Story = {
  args: {
    alertPriority: ALERT_PRIORITY.HIGH,
    measurement: {
      value: 105,
      upperLimit: '100',
      lowerLimit: '90',
    },
  },
};

export const MediumPriority: Story = {
  args: {
    alertPriority: ALERT_PRIORITY.MEDIUM,
    measurement: {
      value: 102,
      upperLimit: '100',
      lowerLimit: '90',
    },
  },
};
export const LowPriority: Story = {
  args: {
    alertPriority: ALERT_PRIORITY.LOW,
    measurement: {
      value: 100.4,
      upperLimit: '100',
      lowerLimit: '90',
    },
  },
};

export const InternalPriority: Story = {
  args: {
    alertPriority: ALERT_PRIORITY.INTERNAL,
    measurement: {
      value: 100.5,
      upperLimit: '100',
      lowerLimit: '90',
    },
  },
};

export const NoPriority: Story = {
  args: {
    alertPriority: undefined,
  },
};
