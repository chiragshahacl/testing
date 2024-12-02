import EmulatorsModal from '@/app/emulator_updates/EmulatorsModal';
import { faker } from '@faker-js/faker';
import { expect } from '@storybook/jest';
import type { Meta, StoryObj } from '@storybook/react';
import { fireEvent, screen } from '@storybook/testing-library';
import { createEmulatorSensor } from './factories/EmulatorSensorFactory';
import { createPatient } from './factories/PatientFactory';

const meta: Meta<typeof EmulatorsModal> = {
  component: EmulatorsModal,
};

export default meta;
type Story = StoryObj<typeof EmulatorsModal>;

export const Default: Story = {
  args: {
    isOpen: true,
    patient: createPatient({ givenName: 'John', familyName: 'Doe' }),
    sensors: faker.helpers.multiple(createEmulatorSensor, { count: 5 }),
  },
  play: async ({ args: { sensors } }) => {
    await expect(screen.getByText('John Doe')).toBeInTheDocument();
    sensors?.forEach(async (sensor) => {
      await expect(
        screen.getByText(`${sensor.type}: ${sensor.primaryIdentifier}`)
      ).toBeInTheDocument();
    });
  },
};

export const Loading: Story = {
  args: {
    isLoading: true,
    isOpen: true,
    patient: createPatient(),
  },
  play: async () => {
    await expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  },
};

export const ChangeMode: Story = {
  args: {
    isOpen: true,
    patient: createPatient(),
    sensors: [
      createEmulatorSensor({
        id: 'sensor1',
        emulators: [
          { name: 'emulator1', currentMode: 'mode1', modes: ['mode1', 'mode2', 'mode3'] },
        ],
      }),
    ],
  },
  play: async ({ args: { onSave } }) => {
    await expect(screen.getByDisplayValue('mode1')).toBeInTheDocument();

    await fireEvent.change(screen.getByDisplayValue('mode1'), { target: { value: 'mode2' } });

    await fireEvent.click(screen.getByText('Save'));

    await expect(onSave).toHaveBeenCalledWith({
      sensor1: {
        emulator1: 'mode2',
      },
    });
  },
};
