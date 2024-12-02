import theme from '@/theme/theme';
import { ThemeProvider } from '@mui/material';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import routeData from 'next/navigation';

import RootLayout from '@/app/(authenticated)/layout';
import { ALERT_AUDIO } from '@/constants';
import { STORAGE_KEYS } from '@/utils/storage';
import AudioManagerContext, { AudioManager } from '@/context/AudioManagerContext';
import PatientsContext from '@/context/PatientsContext';
import SessionContext, { Session } from '@/context/SessionContext';
import { MockBeds, MockGroups, MockPatientMonitors } from '@/utils/groupsMockData';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
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

describe('Authenticated pages -> RootLayout', () => {
  const server = setupServer(
    rest.post('/web/auth/token', (req, res, ctx) => {
      return res(
        ctx.json({
          access: 'access',
          refresh: 'refresh',
          userType: 'non-technical',
        })
      );
    }),
    rest.get('/web/bed', (req, res, ctx) => {
      return res(
        ctx.json({
          resources: MockBeds,
        })
      );
    }),
    rest.get('/web/device', (req, res, ctx) => {
      return res(
        ctx.json({
          resources: MockPatientMonitors,
        })
      );
    }),
    rest.get('/web/bed-group', (req, res, ctx) => {
      return res(
        ctx.json({
          resources: MockGroups,
        })
      );
    })
  );

  beforeAll(() => {
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, 'accessToken');
    localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, 'refreshToken');
    localStorage.setItem(STORAGE_KEYS.USER_TYPE, 'non-technical');

    server.listen();
  });
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  it('renders children', async () => {
    render(
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <SessionContext>
            <AudioManagerContext>
              <PatientsContext>
                <RootLayout>
                  <div data-testid='child' />
                </RootLayout>
              </PatientsContext>
            </AudioManagerContext>
          </SessionContext>
        </QueryClientProvider>
      </ThemeProvider>
    );

    expect(screen.getByTestId('child')).toBeInTheDocument();
  });

  it('prompts user action when auto play is not activated and alarm is enabled', async () => {
    const setAutoPlayActivatedMock = jest.fn();

    render(
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <SessionContext>
            <AudioManager.Provider
              value={{
                audioAlarmSetting: ALERT_AUDIO.ON,
                audioIsActive: true,
                autoPlayActivated: false,
                setAutoPlayActivated: setAutoPlayActivatedMock,
                setTimerIsPaused: jest.fn(),
              }}
            >
              <PatientsContext>
                <RootLayout>
                  <div data-testid='child' />
                </RootLayout>
              </PatientsContext>
            </AudioManager.Provider>
          </SessionContext>
        </QueryClientProvider>
      </ThemeProvider>
    );

    expect(screen.getByText('Audio alarm is enabled')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'OK' }));
    expect(setAutoPlayActivatedMock).toHaveBeenCalledWith(true);
  });

  it('does not prompt user action when auto play is activated and alarm is enabled', async () => {
    render(
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <SessionContext>
            <AudioManager.Provider
              value={{
                audioAlarmSetting: true,
                audioIsActive: true,
                autoPlayActivated: true,
                setAutoPlayActivated: jest.fn(),
                setTimerIsPaused: jest.fn(),
              }}
            >
              <PatientsContext>
                <RootLayout>
                  <div data-testid='child' />
                </RootLayout>
              </PatientsContext>
            </AudioManager.Provider>
          </SessionContext>
        </QueryClientProvider>
      </ThemeProvider>
    );

    expect(screen.queryByText('Audio alarm is enabled')).not.toBeInTheDocument();
  });

  it('does not prompt user action when auto play is not activated and alarm is disabled', async () => {
    render(
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <SessionContext>
            <AudioManager.Provider
              value={{
                audioAlarmSetting: false,
                audioIsActive: true,
                autoPlayActivated: true,
                setAutoPlayActivated: jest.fn(),
                setTimerIsPaused: jest.fn(),
              }}
            >
              <PatientsContext>
                <RootLayout>
                  <div data-testid='child' />
                </RootLayout>
              </PatientsContext>
            </AudioManager.Provider>
          </SessionContext>
        </QueryClientProvider>
      </ThemeProvider>
    );

    expect(screen.queryByText('Audio alarm is enabled')).not.toBeInTheDocument();
  });

  it('shows setting side bar on user action', async () => {
    server.use(
      rest.get('/web/bed-group', (req, res, ctx) => {
        return res(
          ctx.status(200),
          ctx.json({
            resources: MockGroups,
          })
        );
      }),
      rest.get('/web/bed', (req, res, ctx) => {
        return res(
          ctx.status(200),
          ctx.json({
            resources: MockBeds,
          })
        );
      }),
      rest.get('/web/device', (req, res, ctx) => {
        return res(
          ctx.status(200),
          ctx.json({
            resources: MockPatientMonitors,
          })
        );
      })
    );

    render(
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <SessionContext>
            <AudioManagerContext>
              <PatientsContext>
                <RootLayout>
                  <div data-testid='child' />
                </RootLayout>
              </PatientsContext>
            </AudioManagerContext>
          </SessionContext>
        </QueryClientProvider>
      </ThemeProvider>
    );

    expect(screen.getByTestId('settings-component')).not.toBeVisible();
    if (screen.queryByRole('button', { name: 'OK' })) {
      fireEvent.click(screen.getByRole('button', { name: 'OK' }));
    }
    expect(screen.getByRole('button', { name: 'Settings' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Settings' }));
    expect(screen.getByTestId('settings-component')).toBeVisible();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.8.1.20
   */
  it('logs out when unauthenticated', async () => {
    const replaceMock = jest.fn().mockImplementation(() => null);
    jest.spyOn(routeData, 'useRouter').mockImplementation(() => ({
      replace: replaceMock,
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <Session.Provider
          value={{
            accessToken: null,
            refreshToken: null,
            authenticating: false,
          }}
        >
          <AudioManager.Provider
            value={{
              audioAlarmSetting: true,
              audioIsActive: true,
              autoPlayActivated: true,
              setAutoPlayActivated: jest.fn(),
              setTimerIsPaused: jest.fn(),
            }}
          >
            <PatientsContext>
              <RootLayout>
                <div data-testid='child' />
              </RootLayout>
            </PatientsContext>
          </AudioManager.Provider>
        </Session.Provider>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(replaceMock).toHaveBeenCalledWith('/login');
    });
  });
});
