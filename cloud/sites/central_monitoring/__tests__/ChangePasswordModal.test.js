import ChangePasswordModal from '@/components/modals/ChangePasswordModal';
import RuntimeConfigProvider from '@/context/RuntimeContext';
import SessionContext from '@/context/SessionContext';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 0,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
    },
  },
});

const server = setupServer(
  rest.post('/web/auth/change-password', (req, res, ctx) => {
    return res(ctx.status(204));
  }),
  rest.post('/web/auth/token', (req, res, ctx) => {
    return res(
      ctx.json({
        access: 'access',
        refresh: 'refresh',
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Change Password Modal', () => {
  it('renders all components', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <ChangePasswordModal
            currentPassword='currentPassword'
            isOpen
            onClose={() => undefined}
            onSuccess={() => undefined}
          />
        </SessionContext>
      </QueryClientProvider>
    );

    expect(
      screen.getByRole('heading', {
        name: /Change password/i,
      })
    ).toBeInTheDocument();
    expect(screen.getByText('Please enter the new password.')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('New password')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Re-enter new password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Confirm' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Confirm' }).disabled).toBeTruthy();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.1.5.8
   */
  it('validates new password input field', async () => {
    const submitMock = jest.fn();
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <ChangePasswordModal
            isOpen
            currentPassword='currentPassword'
            onClose={() => undefined}
            onSuccess={submitMock}
          />
        </SessionContext>
      </QueryClientProvider>
    );

    fireEvent.focus(screen.getByPlaceholderText('New password'));
    fireEvent.focusOut(screen.getByPlaceholderText('New password'));
    await waitFor(() => {
      expect(screen.getByText('Password is required.')).toBeInTheDocument();
    });
    expect(screen.getByRole('button', { name: 'Confirm' }).disabled).toBeTruthy();

    fireEvent.change(screen.getByPlaceholderText('New password'), {
      target: { value: 'inv' },
    });
    await waitFor(() => {
      expect(screen.getByText('Password does not meet criteria.')).toBeInTheDocument();
    });
    expect(screen.getByRole('button', { name: 'Confirm' }).disabled).toBeTruthy();
  });

  it('validates re-entered password input field', async () => {
    const submitMock = jest.fn();
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <ChangePasswordModal
            currentPassword='currentPassword'
            isOpen
            onClose={() => undefined}
            onSuccess={submitMock}
          />
        </SessionContext>
      </QueryClientProvider>
    );

    fireEvent.change(screen.getByPlaceholderText('New password'), {
      target: { value: 'password' },
    });
    fireEvent.focus(screen.getByPlaceholderText('Re-enter new password'));
    fireEvent.change(screen.getByPlaceholderText('Re-enter new password'), {
      target: { value: 'otherPassword' },
    });
    fireEvent.focusOut(screen.getByPlaceholderText('Re-enter new password'));
    await waitFor(() => {
      expect(screen.getByText('Password does not match previous entry.')).toBeInTheDocument();
    });
    expect(screen.getByRole('button', { name: 'Confirm' }).disabled).toBeTruthy();
  });

  it('handles submit', async () => {
    server.use(
      rest.post('/web/auth/change-password', (req, res, ctx) => {
        return res(ctx.status(204));
      })
    );

    const onSuccessMock = jest.fn();
    render(
      <QueryClientProvider client={queryClient}>
        <RuntimeConfigProvider>
          <SessionContext>
            <ChangePasswordModal
              currentPassword='currentPassword'
              isOpen
              onClose={() => undefined}
              onSuccess={onSuccessMock}
            />
          </SessionContext>
        </RuntimeConfigProvider>
      </QueryClientProvider>
    );

    fireEvent.change(screen.getByPlaceholderText('New password'), {
      target: { value: 'Password1!' },
    });
    fireEvent.change(screen.getByPlaceholderText('Re-enter new password'), {
      target: { value: 'Password1!' },
    });
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Confirm' })).not.toBeDisabled();
    });
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));

    await waitFor(
      () => {
        expect(onSuccessMock).toHaveBeenCalled();
      },
      { timeout: 2000 }
    );
  });
});
