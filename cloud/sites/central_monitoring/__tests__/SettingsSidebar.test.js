import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import routeData from 'next/navigation';

import SettingsSidebar from '@/components/Settings/Sidebar';
import AudioManagerContext, { AudioManager } from '@/context/AudioManagerContext';
import PatientsContext, { PatientsData } from '@/context/PatientsContext';
import RuntimeConfigProvider from '@/context/RuntimeContext';
import SessionContext from '@/context/SessionContext';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.post(
    '/web/auth/token/logout',
    (req, res, ctx) => {
      return res(ctx.status(204));
    },
    rest.post('/web/auth/change-password', (req, res, ctx) => {
      return res(ctx.status(204));
    }),
    rest.post('/web/auth/token', (req, res, ctx) => {
      return res(ctx.status(200));
    })
  )
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 0,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
    },
  },
});

jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      replace: jest.fn(() => null),
    };
  },
  useSearchParams() {
    return undefined;
  },
}));

describe('Settings Component', () => {
  /*
   * Requirement IDs: RQ-00022-B: SR-1.1.4.1, SR-1.1.5.1, SR-1.1.6.8
   */
  it('renders all components', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <RuntimeConfigProvider>
          <SessionContext>
            <PatientsContext>
              <AudioManagerContext>
                <SettingsSidebar />
              </AudioManagerContext>
            </PatientsContext>
          </SessionContext>
        </RuntimeConfigProvider>
      </QueryClientProvider>
    );

    expect(screen.getByText('Admin')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Log out' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Change password' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Manage audio alarm' })).toBeInTheDocument();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.1.6.10, SR-1.1.6.12
   */
  it('open audio manager', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <RuntimeConfigProvider>
          <SessionContext>
            <PatientsContext>
              <AudioManagerContext>
                <SettingsSidebar />
              </AudioManagerContext>
            </PatientsContext>
          </SessionContext>
        </RuntimeConfigProvider>
      </QueryClientProvider>
    );

    expect(screen.getByRole('button', { name: 'Manage audio alarm' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Manage audio alarm' }));
    await waitFor(() => {
      expect(screen.getByTestId('audio_on')).toBeInTheDocument();
    });
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.1.4.1, SR-1.1.4.2, SR-1.1.4.3, SR-1.1.4.4
   */
  it('logs out and pauses audio', async () => {
    const stopAlertSoundMock = jest.fn();
    const setAudioDisabledTimerMock = jest.fn();
    const setAudioIsActiveMock = jest.fn();
    const removeFromBedsDisplayMock = jest.fn();
    const replaceMock = jest.fn().mockImplementation(() => null);
    jest.spyOn(routeData, 'useRouter').mockImplementation(() => ({
      replace: replaceMock,
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <RuntimeConfigProvider>
          <SessionContext>
            <PatientsData.Provider
              value={{
                removeSelfFromBedsDisplayGroup: removeFromBedsDisplayMock,
              }}
            >
              <AudioManager.Provider
                value={{
                  stopAlertSound: stopAlertSoundMock,
                  setAudioDisabledTimer: setAudioDisabledTimerMock,
                  setAudioIsActive: setAudioIsActiveMock,
                }}
              >
                <SettingsSidebar />
              </AudioManager.Provider>
            </PatientsData.Provider>
          </SessionContext>
        </RuntimeConfigProvider>
      </QueryClientProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: 'Log out' }));
    await waitFor(() => {
      expect(screen.getByText('Please enter the current password.'));
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'password' } });
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Confirm' })).not.toBeDisabled();
    });
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));
    await waitFor(() => {
      expect(removeFromBedsDisplayMock).toHaveBeenCalled();
      expect(stopAlertSoundMock).toHaveBeenCalled();
      expect(replaceMock).toHaveBeenCalledWith('/');
    });
  });

  it('handles server error', async () => {
    server.use(
      rest.post('/web/auth/token/logout', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    render(
      <QueryClientProvider client={queryClient}>
        <RuntimeConfigProvider>
          <SessionContext>
            <PatientsContext>
              <AudioManagerContext>
                <SettingsSidebar />
              </AudioManagerContext>
            </PatientsContext>
          </SessionContext>
        </RuntimeConfigProvider>
      </QueryClientProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: 'Log out' }));
    await waitFor(() => {
      expect(screen.getByText('Please enter the current password.')).toBeInTheDocument();
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'password' } });
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Confirm' })).not.toBeDisabled();
    });
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));
    await waitFor(() => {
      expect(
        screen.getByText('Server error. Please try again in a few minutes.')
      ).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('dismiss-modal'));
    await waitFor(() => {
      expect(screen.queryByText('Please enter the current password.')).not.toBeInTheDocument();
    });
  });

  /*
   * Requirement IDs: 	RQ-00022-B: SR-1.1.1.3
   */
  it('handles account locked', async () => {
    server.use(
      rest.post('/web/auth/token/logout', (req, res, ctx) => {
        return res(ctx.json({ detail: 'Account locked.' }), ctx.status(401));
      })
    );

    render(
      <QueryClientProvider client={queryClient}>
        <RuntimeConfigProvider>
          <SessionContext>
            <PatientsContext>
              <AudioManagerContext>
                <SettingsSidebar />
              </AudioManagerContext>
            </PatientsContext>
          </SessionContext>
        </RuntimeConfigProvider>
      </QueryClientProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: 'Log out' }));
    await waitFor(() => {
      expect(screen.getByText('Please enter the current password.')).toBeInTheDocument();
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'password' } });
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Confirm' })).not.toBeDisabled();
    });
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));
    await waitFor(() => {
      expect(
        screen.getByText('Too many attempts. Please try again in 15 minutes.')
      ).toBeInTheDocument();
    });
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.1.2.3
   */
  it('validates before logout', async () => {
    server.use(
      rest.post('/web/auth/token/logout', (req, res, ctx) => {
        return res(ctx.status(401));
      })
    );

    const replaceMock = jest.fn().mockImplementation(() => null);
    jest.spyOn(routeData, 'useRouter').mockImplementation(() => ({
      back: jest.fn().mockImplementation(() => null),
      forward: jest.fn().mockImplementation(() => null),
      prefetch: jest.fn().mockImplementation(() => null),
      replace: replaceMock,
      refresh: jest.fn().mockImplementation(() => null),
      push: jest.fn().mockImplementation(() => null),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <RuntimeConfigProvider>
          <SessionContext>
            <PatientsContext>
              <AudioManagerContext>
                <SettingsSidebar />
              </AudioManagerContext>
            </PatientsContext>
          </SessionContext>
        </RuntimeConfigProvider>
      </QueryClientProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: 'Log out' }));
    await waitFor(() => {
      expect(screen.getByText('Please enter the current password.'));
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'password' } });
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Confirm' })).not.toBeDisabled();
    });
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));
    await waitFor(() => {
      expect(screen.getByText('Incorrect password. Please try again.')).toBeInTheDocument();
    });
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.1.4.1
   */
  it('handles sever error during password validation', async () => {
    server.use(
      rest.post('/web/auth/token', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    render(
      <QueryClientProvider client={queryClient}>
        <RuntimeConfigProvider>
          <SessionContext>
            <PatientsContext>
              <AudioManagerContext>
                <SettingsSidebar />
              </AudioManagerContext>
            </PatientsContext>
          </SessionContext>
        </RuntimeConfigProvider>
      </QueryClientProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: 'Change password' }));
    await waitFor(() => {
      expect(screen.getByText('Please enter the current password.'));
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'password' } });
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Confirm' })).not.toBeDisabled();
    });
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));
    await waitFor(() => {
      expect(
        screen.getByText('Server error. Please try again in a few minutes.')
      ).toBeInTheDocument();
    });
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.1.5.11 RQ-00022-B: SR-1.1.1.1, SR-1.1.5.10, SR-1.1.5.9 RQ-00022-B: SR-1.1.1.1, SR-1.1.5.11 RQ-00022-B: SR-1.1.1.1, SR-1.1.5.9, SR-1.1.5.12 RQ-00022-B: SR-1.1.5.6, SR-1.1.2.5
   * RQ-00022-B: SR-1.1.1.1, SR-1.1.5.4, SR-1.1.5.13, SR-1.1.5.5, SR-1.1.5.7, SR-1.1.5.15, SR-7.4.1
   */
  it('validates password before changing', async () => {
    server.use(
      rest.post('/web/auth/token', (req, res, ctx) => {
        return res(ctx.status(401));
      })
    );

    render(
      <QueryClientProvider client={queryClient}>
        <RuntimeConfigProvider>
          <SessionContext>
            <PatientsContext>
              <AudioManagerContext>
                <SettingsSidebar />
              </AudioManagerContext>
            </PatientsContext>
          </SessionContext>
        </RuntimeConfigProvider>
      </QueryClientProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: 'Change password' }));
    await waitFor(() => {
      expect(screen.getByText('Please enter the current password.'));
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'password' } });
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Confirm' })).not.toBeDisabled();
    });
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));
    await waitFor(() => {
      expect(screen.getByText('Incorrect password. Please try again.')).toBeInTheDocument();
    });
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.1.5.17 RQ-00022-B: SR-1.1.5.2 RQ-00022-B: SR-1.1.5.4, SR-1.1.5.13, SR-1.1.5.5 RQ-00022-B: SR-1.1.5.16, SR-1.1.5.2
   */
  it('changes password', async () => {
    server.use(
      rest.post('/web/auth/token', (req, res, ctx) => {
        return res(ctx.status(200));
      }),
      rest.post('/web/auth/change-password', (req, res, ctx) => {
        return res(ctx.status(204));
      })
    );

    render(
      <QueryClientProvider client={queryClient}>
        <RuntimeConfigProvider>
          <SessionContext>
            <PatientsContext>
              <AudioManagerContext>
                <SettingsSidebar />
              </AudioManagerContext>
            </PatientsContext>
          </SessionContext>
        </RuntimeConfigProvider>
      </QueryClientProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: 'Change password' }));
    await waitFor(() => {
      expect(screen.getByText('Please enter the current password.'));
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'password' } });
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Confirm' })).not.toBeDisabled();
    });
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));
    await waitFor(() => {
      expect(
        screen.getByRole('heading', {
          name: /Change password/i,
        })
      ).toBeInTheDocument();
    });
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
    await waitFor(() => {
      expect(
        screen.getByRole('heading', {
          name: /Password changed/i,
        })
      ).toBeInTheDocument();
    });
    fireEvent.click(
      screen.getByRole('button', {
        name: 'Ok',
      })
    );
    await waitFor(() => {
      expect(
        screen.queryByRole('heading', {
          name: /Password changed/i,
        })
      ).not.toBeInTheDocument();
    });
  });

  it('changes password -> handles server error', async () => {
    server.use(
      rest.post('/web/auth/token', (req, res, ctx) => {
        return res(ctx.status(200));
      }),
      rest.post('/web/auth/change-password', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    render(
      <QueryClientProvider client={queryClient}>
        <RuntimeConfigProvider>
          <SessionContext>
            <PatientsContext>
              <AudioManagerContext>
                <SettingsSidebar />
              </AudioManagerContext>
            </PatientsContext>
          </SessionContext>
        </RuntimeConfigProvider>
      </QueryClientProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: 'Change password' }));
    await waitFor(() => {
      expect(screen.getByText('Please enter the current password.'));
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'password' } });
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Confirm' })).not.toBeDisabled();
    });
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));
    await waitFor(() => {
      expect(
        screen.getByRole('heading', {
          name: /Change password/i,
        })
      ).toBeInTheDocument();
    });
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
    await waitFor(() => {
      expect(
        screen.getByText('Server error. Please try again in a few minutes.')
      ).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('dismiss-modal'));
    await waitFor(() => {
      expect(screen.queryByText('Please enter the current password.')).not.toBeInTheDocument();
    });
  });
});
