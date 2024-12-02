import SensorIcon from '@/components/cards/SensorCard/SensorIcon';
import { SENSOR_TYPES } from '@/types/sensor';
import type { Meta, StoryObj } from '@storybook/react';

const meta: Meta<typeof SensorIcon> = {
  component: SensorIcon,
  argTypes: { sensorType: { control: 'radio', options: SENSOR_TYPES } },
  title: 'SensorCard/Sensor Icon',
};

export default meta;
type Story = StoryObj<typeof SensorIcon>;

export const Chest: Story = {
  args: {
    sensorType: SENSOR_TYPES.CHEST,
  },
};

export const Adam: Story = {
  args: {
    sensorType: SENSOR_TYPES.ADAM,
  },
};

export const Limb: Story = {
  args: {
    sensorType: SENSOR_TYPES.LIMB,
  },
};

export const Nonin: Story = {
  args: {
    sensorType: SENSOR_TYPES.NONIN,
  },
};

export const BP: Story = {
  args: {
    sensorType: SENSOR_TYPES.BP,
  },
};

export const Thermometer: Story = {
  args: {
    sensorType: SENSOR_TYPES.THERMOMETER,
  },
};

export const PatientMonitor: Story = {
  args: {
    sensorType: SENSOR_TYPES.PATIENT_MONITOR,
  },
};
