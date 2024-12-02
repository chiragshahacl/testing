import ChestTemperature from '@/app/(authenticated)/home/details/Metrics/ChestTemperature';
import { ERROR_VALUE } from '@/constants';
import { ALERT_PRIORITY } from '@/utils/metricCodes';
import { expect } from '@storybook/jest';
import { Meta, StoryObj } from '@storybook/react';
import { waitFor, within } from '@storybook/testing-library';

const meta: Meta<typeof ChestTemperature> = {
  component: ChestTemperature,
  title: 'Metrics/ChestTemperature',
  args: {
    measurement: {
      value: 98.6,
      upperLimit: '100',
      lowerLimit: '90',
    },
    isConnected: true,
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
type Story = StoryObj<typeof ChestTemperature>;

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

export const Error: Story = {
  args: {
    measurement: { value: ERROR_VALUE },
  },
};
export const Celsius: Story = {
  args: {
    unit: '°C',
    measurement: {
      value: 38.5,
      upperLimit: '37.7',
      lowerLimit: '36.1',
    },
  },
};
