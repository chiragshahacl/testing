import PasswordValidationModal from '@/components/modals/PasswordValidationModal';
import { expect, jest } from '@storybook/jest';
import { Meta, StoryObj } from '@storybook/react';
import { screen, userEvent } from '@storybook/testing-library';

const meta: Meta<typeof PasswordValidationModal> = {
  component: PasswordValidationModal,
  args: {
    isOpen: true,
    onBack: jest.fn(),
  },
};

export default meta;
type Story = StoryObj<typeof PasswordValidationModal>;

export const Default: Story = {
  play: async () => {
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByTestId('submit-button');

    await expect(passwordInput).toBeInTheDocument();
    await expect(submitButton).toBeInTheDocument();
    await expect(submitButton).toBeDisabled();
  },
};

export const Filled: Story = {
  play: async () => {
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByTestId('submit-button');

    await expect(submitButton).toBeDisabled();
    await userEvent.type(passwordInput, 'password');
    await expect(submitButton).not.toBeDisabled();
  },
};

export const Submitting: Story = {
  play: async ({ args: { onSubmit } }) => {
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByTestId('submit-button');

    await userEvent.type(passwordInput, 'hi mom');
    await userEvent.click(submitButton);
    await expect(onSubmit).toHaveBeenCalledWith(
      { password: 'hi mom', submit: null },
      expect.anything()
    );
  },
};

export const GoBack: Story = {
  args: {
    onBack: jest.fn(),
  },
  play: async ({ args: { onBack } }) => {
    const backButton = screen.getByTestId('back-to-edit-button');

    await expect(backButton).toBeInTheDocument();
    await userEvent.click(backButton);
    await expect(onBack).toHaveBeenCalled();
  },
};

export const WithCustomDescription: Story = {
  args: {
    description: (
      <div>
        <p>Customized modal description.</p>
        <p>Enter the current password.</p>
      </div>
    ),
  },
  play: async () => {
    const desc1 = screen.getByText('Customized modal description.');
    const desc2 = screen.getByText('Enter the current password.');

    await expect(desc1).toBeInTheDocument();
    await expect(desc2).toBeInTheDocument();
  },
};

export const Closing: Story = {
  play: async ({ args: { onClose } }) => {
    const closeIcon = screen.getByTestId('dismiss-modal');

    await userEvent.click(closeIcon);
    await expect(onClose).toHaveBeenCalled();
  },
};
