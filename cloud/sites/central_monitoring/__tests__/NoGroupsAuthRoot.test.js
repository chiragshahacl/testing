import theme from '@/theme/theme';
import { ThemeProvider } from '@mui/material';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import RootLayout from '@/app/(authenticated)/layout';
import { ALERT_AUDIO } from '@/constants';
import { STORAGE_KEYS } from '@/utils/storage';
import AudioManagerContext, { AudioManager } from '@/context/AudioManagerContext';
import PatientsContext from '@/context/PatientsContext';
import SessionContext from '@/context/SessionContext';
import { MockBeds, MockPatientMonitors } from '@/utils/groupsMockData';
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
      route: '/',
      pathname: '',
      query: '',
      asPath: '',
      push: jest.fn(),
      events: {
        on: jest.fn(),
        off: jest.fn(),
      },
      replace: jest.fn(() => null),
      beforePopState: jest.fn(() => null),
      prefetch: jest.fn(() => null),
    };
  },
  useSearchParams() {
    return undefined;
  },
}));

describe('no beds in system', () => {
  const server = setupServer(
    rest.post('/web/auth/token', (req, res, ctx) => {
      return res(
        ctx.json({
          access: 'access',
          refresh: 'refresh',
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
    rest.get('/web/bed', (req, res, ctx) => {
      return res(
        ctx.json({
          resources: MockBeds,
        })
      );
    }),
    rest.get('/web/bed-group', (req, res, ctx) => {
      return res(
        ctx.json({
          resources: [],
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
  afterAll(() => server.close());

  /*
   * Requirement IDs: RQ-00022-B: SR-1.2.4.2
   */
  it('shows group management modal when open', async () => {
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

    await waitFor(() => {
      expect(screen.getByTestId('Group Management-modal')).toBeInTheDocument();
      expect(screen.queryByTestId('Bed Management-modal')).not.toBeInTheDocument();
    });
  });

  it('hides group management modal on user action', async () => {
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
                setAudioDisabledTimer: jest.fn(),
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

    await new Promise(process.nextTick);
    await waitFor(() => {
      expect(screen.getByTestId('Group Management-modal')).toBeInTheDocument();
      expect(screen.queryByTestId('Bed Management-modal')).not.toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('dismiss-modal'));
    await waitFor(() => {
      expect(setAutoPlayActivatedMock).toHaveBeenCalledWith(true);
    });
  });
});
