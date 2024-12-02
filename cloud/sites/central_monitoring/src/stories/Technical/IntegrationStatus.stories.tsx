import { Meta, StoryObj } from '@storybook/react';
import IntegrationStatus from '@/components/modals/technical/IntegrationStatus';
import { screen } from '@storybook/testing-library';
import { expect } from '@storybook/jest';

const meta: Meta<typeof IntegrationStatus> = {
  title: 'Technical/Components/IntegrationStatus',
  component: IntegrationStatus,
  argTypes: {
    open: { control: 'boolean' },
    handleClose: { action: 'handleClose' },
    successStatus: { control: 'boolean' },
  },
};

export default meta;
type Story = StoryObj<typeof IntegrationStatus>;

export const Success: Story = {
  args: {
    open: true,
    successStatus: true,
  },
  play: async () => {
    expect(screen.getByText('Integration Completed')).toBeInTheDocument();
  },
};

export const Failure: Story = {
  args: {
    open: true,
    successStatus: false,
  },
  play: async () => {
    expect(screen.getByText('Integration Failed')).toBeInTheDocument();
  },
};

export const Closed: Story = {
  args: {
    open: false,
  },
};
