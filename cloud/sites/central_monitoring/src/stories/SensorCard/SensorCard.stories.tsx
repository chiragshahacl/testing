import type { Meta, StoryObj } from '@storybook/react';

import SensorCard from '@/components/cards/SensorCard/SensorCard';
import { SENSOR_TYPES } from '@/types/sensor';
import { ALERT_PRIORITY, ALERT_TYPES, DEVICE_ALERT_CODES } from '@/utils/metricCodes';

const meta: Meta<typeof SensorCard> = {
  component: SensorCard,
  argTypes: {
    battery: { control: { type: 'range', min: 0, max: 100, step: 1 } },
    signal: { control: { type: 'range', min: -100, max: 0, step: 1 } },
    sensorType: { control: { type: 'select', options: SENSOR_TYPES } },
  },
  title: 'SensorCard/SensorCard',
};

export default meta;
type Story = StoryObj<typeof SensorCard>;

export const ChestSensorCard: Story = {
  args: {
    sensorType: SENSOR_TYPES.CHEST,
    title: 'ANNE Chest',
    id: 'SEN-EM-001',
    isLoading: false,
    hasSensorFailure: false,
    hasSensorSignalAlert: false,
  },
};

export const ChestSensorCardWithSensorFailure: Story = {
  args: {
    sensorType: SENSOR_TYPES.CHEST,
    title: 'ANNE Chest',
    id: 'SEN-EM-001',
    isLoading: false,
    hasSensorFailure: true,
    hasSensorSignalAlert: false,
    alert: {
      type: ALERT_TYPES.DEVICE,
      id: 'A-001',
      code: DEVICE_ALERT_CODES.SENSOR_FAILURE_ALERT.code,
      deviceCode: 'ANNE Chest',
      priority: ALERT_PRIORITY.HIGH,
      acknowledged: false,
      timestamp: '0000',
    },
  },
};

export const ChestSensorCardWithAlert: Story = {
  args: {
    sensorType: SENSOR_TYPES.CHEST,
    title: 'ANNE Chest',
    id: 'SEN-EM-001',
    isLoading: false,
    hasSensorFailure: false,
    hasSensorSignalAlert: false,
    alert: {
      type: ALERT_TYPES.DEVICE,
      id: 'A-001',
      code: DEVICE_ALERT_CODES.LOW_SIGNAL_ALERT.code,
      deviceCode: 'ANNE Chest',
      priority: ALERT_PRIORITY.LOW,
      acknowledged: false,
      timestamp: '0000',
    },
  },
};
export const ChestSensorCardIsLoading: Story = {
  args: {
    title: 'ANNE Chest',
    id: 'SEN-EM-001',
    sensorType: SENSOR_TYPES.CHEST,
    isLoading: true,
    hasSensorFailure: false,
    hasSensorSignalAlert: false,
  },
};
