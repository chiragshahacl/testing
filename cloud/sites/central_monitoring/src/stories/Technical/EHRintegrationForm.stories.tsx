import { expect, jest } from '@storybook/jest';
import { Meta, StoryObj } from '@storybook/react';
import { screen } from '@storybook/testing-library';
import EHRintegrationForm from '@/app/technical/home/EHRintegrationForm';

const meta: Meta<typeof EHRintegrationForm> = {
  component: EHRintegrationForm,
  title: 'Technical/EHRintegrationForm',
};

export default meta;
type Story = StoryObj<typeof EHRintegrationForm>;

export const Default: Story = {
  args: {
    setValues: jest.fn(),
    startFormProcessing: jest.fn(),
    isIntegrationSuccess: false,
    isIntegrationComplete: false,
    hideIntegrationStatus: jest.fn(),
    submitDisabled: true,
    setSubmitDisabled: jest.fn(),
    setValidPassword: jest.fn(),
  },
  play: async () => {
    const hostField = screen.getByTestId('host');
    const portField = screen.getByTestId('port');
    const intervalField = screen.getByTestId('interval');

    expect(hostField).toBeInTheDocument();
    expect(portField).toBeInTheDocument();
    expect(intervalField).toBeInTheDocument();
  },
};
