import BodyTemperature from '@/app/(authenticated)/home/details/Metrics/BodyTemperature';
import { ERROR_VALUE } from '@/constants';
import { ALERT_PRIORITY } from '@/utils/metricCodes';
import { expect } from '@storybook/jest';
import { Meta, StoryObj } from '@storybook/react';
import { waitFor, within } from '@storybook/testing-library';

const meta: Meta<typeof BodyTemperature> = {
  component: BodyTemperature,
  title: 'Metrics/BodyTemperature',
  argTypes: {
    timestamp: { control: 'date' },
  },
  args: {
    isConnected: true,
    isLoading: false,
    timestamp: Date.now().toString(),
    measurement: {
      value: 98.6,
      lowerLimit: '93.2',
      upperLimit: '102.3',
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
type Story = StoryObj<typeof BodyTemperature>;

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

export const NoValue: Story = {
  args: {
    measurement: {
      value: undefined,
    },
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

export const TwoHoursAgo: Story = {
  args: {
    timestamp: (Date.now() - 2 * 3600000).toString(),
  },
};
