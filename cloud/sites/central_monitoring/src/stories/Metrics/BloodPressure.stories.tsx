import BloodPressure from '@/app/(authenticated)/home/details/Metrics/BloodPressure';
import { ALERT_PRIORITY } from '@/utils/metricCodes';
import { expect } from '@storybook/jest';
import { Meta, StoryObj } from '@storybook/react';
import { waitFor, within } from '@storybook/testing-library';

const meta: Meta<typeof BloodPressure> = {
  component: BloodPressure,
  title: 'Metrics/BloodPressure',
  argTypes: {
    timestamp: { control: 'date' },
  },
  args: {
    isConnected: true,
    isLoading: false,
    diastolicMeasurement: {
      value: 73,
      upperLimit: '160',
      lowerLimit: '90',
    },
    systolicMeasurement: {
      value: 130,
      upperLimit: '110',
      lowerLimit: '50',
    },
    mapMeasurement: 126,

    unit: 'mmHg',
    timestamp: Date.now().toString(),
  },
  play: async ({
    canvasElement,
    args: { diastolicMeasurement, systolicMeasurement, alertPriority, mapMeasurement },
  }) => {
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
        if (systolicMeasurement.value) {
          const systolic = canvas.getByText(systolicMeasurement.value);
          expect(systolic).toHaveStyle('color: #000000');
        }
        if (systolicMeasurement.upperLimit) {
          const systolicUpper = canvas.getByText(systolicMeasurement.upperLimit);
          expect(systolicUpper).toHaveStyle('color: #000000');
        }
        if (systolicMeasurement.lowerLimit) {
          const systolcLower = canvas.getByText(systolicMeasurement.lowerLimit);
          expect(systolcLower).toHaveStyle('color: #000000');
        }

        if (diastolicMeasurement.value) {
          const diastolic = canvas.getByText(diastolicMeasurement.value);
          expect(diastolic).toHaveStyle('color: #000000');
        }
        if (diastolicMeasurement.upperLimit) {
          const diastolicUpper = canvas.getByText(diastolicMeasurement.upperLimit);
          expect(diastolicUpper).toHaveStyle('color: #000000');
        }
        if (diastolicMeasurement.lowerLimit) {
          const diastolicLower = canvas.getByText(diastolicMeasurement.lowerLimit);
          expect(diastolicLower).toHaveStyle('color: #000000');
        }

        if (mapMeasurement) {
          const map = canvas.getByText(mapMeasurement);
          expect(map).toHaveStyle('color: #000000');
        }
      });
    }
  },
};

export default meta;
type Story = StoryObj<typeof BloodPressure>;

export const Loading: Story = {
  args: {
    isLoading: true,
  },
};

export const SystolicError: Story = {
  args: {
    systolicError: true,
  },
};

export const DiastolicError: Story = {
  args: {
    diastolicError: true,
  },
};

export const MapError: Story = {
  args: {
    mapError: true,
  },
};

export const NoValue: Story = {
  args: {
    diastolicMeasurement: {
      value: undefined,
    },
    systolicMeasurement: {
      value: undefined,
    },
    mapMeasurement: undefined,
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

export const TechnicalError: Story = {
  args: {
    measureFailed: true,
  },
};
