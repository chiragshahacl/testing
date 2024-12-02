import EHRconfirmationModal from '@/components/modals/technical/EHRconfirmation';
import { Meta, StoryObj } from '@storybook/react';
import { expect, jest } from '@storybook/jest';
import { userEvent, screen } from '@storybook/testing-library';

const onBackToEdit = jest.fn();
const onConfirm = jest.fn();

const meta: Meta<typeof EHRconfirmationModal> = {
  title: 'Technical/Components/EHRconfirmationModal',
  component: EHRconfirmationModal,
  argTypes: {
    isOpen: { control: 'boolean' },
    host: { control: 'text' },
    port: { control: 'number' },
    interval: { control: 'number' },
    onBackToEdit: { action: 'onBackToEdit' },
    onConfirm: { action: 'onConfirm' },
  },
};

export default meta;
type Story = StoryObj<typeof EHRconfirmationModal>;

export const Default: Story = {
  args: {
    isOpen: true,
    host: 'localhost',
    port: 0,
    interval: 1,
    onBackToEdit: jest.fn(),
    onConfirm: jest.fn(),
  },
};

export const Confirm: Story = {
  args: {
    isOpen: true,
    host: 'example.com',
    port: 8080,
    interval: 15,
    onBackToEdit: onBackToEdit,
    onConfirm: onConfirm,
  },
  play: async () => {
    const ConfirmButton = screen.getByTestId('confirm-button');

    expect(ConfirmButton).toBeInTheDocument();
    await userEvent.click(ConfirmButton);
    expect(onConfirm).toBeCalled();
  },
};

export const BackToEdit: Story = {
  args: {
    isOpen: true,
    host: 'example.com',
    port: 8080,
    interval: 15,
    onBackToEdit: onBackToEdit,
    onConfirm: onConfirm,
  },
  play: async () => {
    const BackToEditButton = screen.getByTestId('back-to-edit-button');

    expect(BackToEditButton).toBeInTheDocument();
    await userEvent.click(BackToEditButton);
    expect(onBackToEdit).toBeCalled();
  },
};

export const Closed: Story = {
  args: {
    isOpen: false,
    host: 'example.com',
    port: 8080,
    interval: 15,
  },
};
