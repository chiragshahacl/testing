import { expect, jest } from '@storybook/jest';
import { Meta, StoryObj } from '@storybook/react';
import { userEvent, waitFor, within } from '@storybook/testing-library';
import { rest } from 'msw';
import Login from '../app/login/page';
import { STORAGE_KEYS } from '@/utils/storage';
import { Suspense } from 'react';
import { I18nextProvider } from 'react-i18next';
import i18n from '@/app/i18n';

const onReplace = jest.fn();

const withI18next = (Story: any) => {
  return (
    // This catches the suspense from components not yet ready (still loading translations)
    // Alternative: set useSuspense to false on i18next.options.react when initializing i18next
    <Suspense fallback={<div>loading translations...</div>}>
      <I18nextProvider i18n={i18n}>
        <Story />
      </I18nextProvider>
    </Suspense>
  );
};

const meta: Meta<typeof Login> = {
  component: Login,
  title: 'Login/Form',
  decorators: [
    withI18next,
    (Story) => {
      onReplace.mockReset();
      localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
      return <Story />;
    },
  ],
  parameters: {
    nextjs: {
      navigation: {
        replace(href: string) {
          onReplace(href);
          return Promise.resolve(true);
        },
      },
    },
    msw: {
      handlers: [
        rest.post('/web/auth/token', (req, res, ctx) => {
          return res(
            ctx.json({
              access: 'access',
              token: 'token',
            })
          );
        }),
      ],
    },
  },
};

export default meta;
type Story = StoryObj<typeof Login>;

export const Default: Story = {};

/*
 * Requirement IDs: RQ-00022-B: SR-1.1.3.4
 */
export const SuccessfulLogin: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const passwordInput = canvas.getByPlaceholderText('Password');
    const loginButton = canvas.getByTestId('login-button');

    expect(passwordInput).toBeInTheDocument();
    expect(loginButton).toBeInTheDocument();
    expect(loginButton).toBeDisabled();

    await userEvent.type(passwordInput, 'correctPassword');

    expect(loginButton).not.toBeDisabled();

    await waitFor(() => {
      userEvent.click(loginButton, { pointerEventsCheck: 0 }); // Bypasses pointer-events: none
      expect(onReplace).toHaveBeenCalledWith('/home');
    });
  },
};

/*
 * Requirement IDs: RQ-00022-B: SR-1.8.1.20 RQ-00022-B: SR-1.1.3.6
 */
export const IncorrectPassword: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.post('/web/auth/token', (req, res, ctx) => {
          return res(ctx.status(401));
        }),
      ],
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const passwordInput = canvas.getByPlaceholderText('Password');
    const loginButton = canvas.getByRole('button', { name: 'Log in' });

    await waitFor(() => userEvent.click(passwordInput));
    await userEvent.type(passwordInput, 'incorrectPassword');
    await waitFor(() => expect(loginButton).not.toBeDisabled());
    await waitFor(() => userEvent.click(loginButton));

    await waitFor(() =>
      expect(canvas.getByText('Incorrect password. Please try again.')).toBeInTheDocument()
    );
    await waitFor(() => expect(onReplace).not.toHaveBeenCalled());
  },
};

/*
 * Requirement IDs: RQ-00022-B: SR-1.1.3.6
 */
export const InvalidPassword: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.post('/web/auth/token', (req, res, ctx) => {
          return res(ctx.status(422));
        }),
      ],
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const passwordInput = canvas.getByPlaceholderText('Password');
    const loginButton = canvas.getByRole('button', { name: 'Log in' });

    await waitFor(() => userEvent.click(passwordInput));
    await userEvent.type(passwordInput, ' ');
    await waitFor(() => expect(loginButton).not.toBeDisabled());
    await waitFor(() => userEvent.click(loginButton));

    await waitFor(() =>
      expect(canvas.getByText('Incorrect password. Please try again.')).toBeInTheDocument()
    );
    await waitFor(() => expect(onReplace).not.toHaveBeenCalled());
  },
};

export const TooManyAttemps: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.post('/web/auth/token', (req, res, ctx) => {
          return res(ctx.status(429));
        }),
      ],
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const passwordInput = canvas.getByPlaceholderText('Password');
    const loginButton = canvas.getByRole('button', { name: 'Log in' });

    await waitFor(() => userEvent.click(passwordInput));
    await userEvent.type(passwordInput, 'tooManyAttempts');
    await waitFor(() => expect(loginButton).not.toBeDisabled());
    await waitFor(() => userEvent.click(loginButton));

    await waitFor(() =>
      expect(
        canvas.getByText('Too many attempts. Please try again in 15 minutes.')
      ).toBeInTheDocument()
    );
    await waitFor(() => expect(onReplace).not.toHaveBeenCalled());
  },
};

/*
 * Requirement IDs: RQ-00022-B: SR-1.1.1.3
 */
export const AccountLocked: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.post('/web/auth/token', (req, res, ctx) => {
          return res(ctx.status(403));
        }),
      ],
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const passwordInput = canvas.getByPlaceholderText('Password');
    const loginButton = canvas.getByRole('button', { name: 'Log in' });

    await waitFor(() => userEvent.click(passwordInput));
    await userEvent.type(passwordInput, 'tooManyAttempts');
    await waitFor(() => expect(loginButton).not.toBeDisabled());
    await waitFor(() => userEvent.click(loginButton));

    await waitFor(() =>
      expect(
        canvas.getByText('Too many attempts. Please try again in 15 minutes.')
      ).toBeInTheDocument()
    );
    await waitFor(() => expect(onReplace).not.toHaveBeenCalled());
  },
};

export const ServerError: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.post('/web/auth/token', (req, res, ctx) => {
          return res(ctx.status(500));
        }),
      ],
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const passwordInput = canvas.getByPlaceholderText('Password');
    const loginButton = canvas.getByRole('button', { name: 'Log in' });

    await waitFor(() => userEvent.click(passwordInput));
    await userEvent.type(passwordInput, 'tooManyAttempts');
    await waitFor(() => expect(loginButton).not.toBeDisabled());
    await waitFor(() => userEvent.click(loginButton));

    await waitFor(() =>
      expect(
        canvas.getByText('Server error. Please try again in a few minutes.')
      ).toBeInTheDocument()
    );
    await waitFor(() => expect(onReplace).not.toHaveBeenCalled());
  },
};
