import { expect } from '@storybook/jest';
import type { Meta, StoryObj } from '@storybook/react';
import { fireEvent, screen, userEvent, waitFor } from '@storybook/testing-library';

import ChangePasswordModal from '@/components/modals/ChangePasswordModal';
import { rest } from 'msw';

const meta: Meta<typeof ChangePasswordModal> = {
  component: ChangePasswordModal,
  args: {
    isOpen: true,
  },
  parameters: {
    msw: {
      handlers: [
        rest.post('/web/auth/change-password', (req, res, ctx) => {
          return res(ctx.status(204));
        }),
      ],
    },
  },
};

export default meta;
type Story = StoryObj<typeof ChangePasswordModal>;

export const EmptyForm: Story = {
  play: async () => {
    fireEvent.focusOut(screen.getByPlaceholderText('New password'));
    fireEvent.focusOut(screen.getByPlaceholderText('Re-enter new password'));

    await waitFor(() => {
      expect(screen.getByText('Password is required.')).toBeInTheDocument();
      expect(screen.getByText('This field is required')).toBeInTheDocument();
    });
  },
};

export const FilledWithValidData: Story = {
  play: async () => {
    await userEvent.type(screen.getByPlaceholderText('New password'), 'newPassword@123');
    await userEvent.type(screen.getByPlaceholderText('Re-enter new password'), 'newPassword@123');

    await userEvent.click(screen.getByRole('button', { name: 'Confirm' }), {
      pointerEventsCheck: 0,
    });
  },
};

export const InvalidNewPassword: Story = {
  play: async () => {
    await userEvent.type(screen.getByPlaceholderText('New password'), 'inv');
    fireEvent.focusOut(screen.getByPlaceholderText('New password'));

    await waitFor(() => {
      expect(screen.getByText('Password does not meet criteria.')).toBeInTheDocument();
    });
  },
};

export const InvalidReenteredPassword: Story = {
  play: async () => {
    await userEvent.type(screen.getByPlaceholderText('New password'), 'newPassword123!');
    await userEvent.type(
      screen.getByPlaceholderText('Re-enter new password'),
      'mismatchedPassword'
    );
    fireEvent.focusOut(screen.getByPlaceholderText('Re-enter new password'));
    await userEvent.click(screen.getByRole('button', { name: 'Confirm' }), {
      pointerEventsCheck: 0,
    });

    await waitFor(() => {
      expect(screen.getByText('Password does not match previous entry.')).toBeInTheDocument();
    });
  },
};

/*
 * Requirement IDs: RQ-00022-B:SR-1.1.1.1, SR-1.1.5.14
 */
export const ServerError: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.post('/web/auth/change-password', (req, res, ctx) => {
          return res(ctx.status(500));
        }),
      ],
    },
  },
  play: async (context) => {
    await FilledWithValidData.play?.(context);

    await waitFor(() => {
      expect(
        screen.getByText('Server error. Please try again in a few minutes.')
      ).toBeInTheDocument();
    });
  },
};
