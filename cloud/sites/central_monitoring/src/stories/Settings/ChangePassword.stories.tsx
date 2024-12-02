import ChangePassword from '@/components/Settings/ChangePassword';
import { expect } from '@storybook/jest';
import type { Meta, StoryObj } from '@storybook/react';
import { fireEvent, screen, userEvent, waitFor } from '@storybook/testing-library';

import { rest } from 'msw';

const meta: Meta<typeof ChangePassword> = {
  component: ChangePassword,
  args: {
    isOpen: true,
  },
  parameters: {
    msw: {
      handlers: [
        rest.post('/web/auth/token', (req, res, ctx) => {
          return res(ctx.status(204));
        }),
        rest.post('/web/auth/change-password', (req, res, ctx) => {
          return res(ctx.status(204));
        }),
      ],
    },
  },
};

export default meta;
type Story = StoryObj<typeof ChangePassword>;

export const Default: Story = {};

export const ValidPassword: Story = {
  play: async ({ args: { onClose } }) => {
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByTestId('submit-button');

    await userEvent.type(passwordInput, 'hi mom');
    await userEvent.click(submitButton, { pointerEventsCheck: 0 });

    await waitFor(() => {
      expect(screen.getByPlaceholderText('New password')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Re-enter new password')).toBeInTheDocument();
    });

    await fireEvent.focus(screen.getByPlaceholderText('New password'));
    await userEvent.type(screen.getByPlaceholderText('New password'), 'newPassword@123');

    await fireEvent.focus(screen.getByPlaceholderText('Re-enter new password'));
    await userEvent.type(screen.getByPlaceholderText('Re-enter new password'), 'newPassword@123');

    await userEvent.click(screen.getByRole('button', { name: 'Confirm' }), {
      pointerEventsCheck: 0,
    });

    await waitFor(() => {
      expect(screen.getByText('Password changed')).toBeInTheDocument();
      expect(
        screen.getByText(
          'Your password has been successfully changed. Please use your new password for future logins.'
        )
      ).toBeInTheDocument();
    });
    await userEvent.click(screen.getByRole('button', { name: 'Ok' }));
    await expect(onClose).toHaveBeenCalled();
  },
};

export const InvalidPassword: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.post('/web/auth/token', (req, res, ctx) => {
          return res(ctx.status(401));
        }),
      ],
    },
  },
  play: async () => {
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByTestId('submit-button');

    await userEvent.type(passwordInput, 'hi mom');
    await userEvent.click(submitButton, { pointerEventsCheck: 0 });
    await waitFor(() => {
      expect(screen.getByText('Incorrect password. Please try again.')).toBeInTheDocument();
    });
  },
};

/*
 * Requirement IDs: RQ-00022-B: SR-1.1.5.17
 */
export const Closing: Story = {
  play: async ({ args: { onClose } }) => {
    const closeIcon = screen.getByTestId('dismiss-modal');

    await userEvent.click(closeIcon);
    await expect(onClose).toHaveBeenCalled();
  },
};
