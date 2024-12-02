import { render, screen, waitFor } from '@testing-library/react';
import moment from 'moment';

import SystemStatusBar from '@/components/layout/SystemStatusBar';
import PatientsContext from '@/context/PatientsContext';
import RuntimeConfigProvider from '@/context/RuntimeContext';
import SessionContext from '@/context/SessionContext';
import { STORAGE_KEYS } from '@/utils/storage';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { MockPatientMonitors } from '@/utils/groupsMockData';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 0,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
    },
  },
});

jest.mock('../src/utils/runtime', () => ({
  getCachedRuntimeConfig: () => ({
    APP_URL: 'https://api.dev.tucana.sibel.health',
    HOSPITAL_TZ: 'UTC',
    // eslint-disable-next-line
    HOSPITAL_TITLE: "Children's Hospital",
    HEALTHCHECK_INTERVAL: 100,
    MAX_NUMBER_BEDS: 64,
  }),
}));

const server = setupServer(
  rest.post('https://api.dev.tucana.sibel.health/web/auth/token', (req, res, ctx) => {
    return res(
      ctx.json({
        access: 'access',
        refresh: 'refresh',
      })
    );
  }),
  rest.get('https://api.dev.tucana.sibel.health/web/bed', (req, res, ctx) => {
    return res(ctx.status(200));
  }),
  rest.get('https://api.dev.tucana.sibel.health/web/device', (req, res, ctx) => {
    return res(
      ctx.json({
        resources: MockPatientMonitors,
      })
    );
  }),
  rest.get('https://api.dev.tucana.sibel.health/web/bed-group', (req, res, ctx) => {
    return res(ctx.status(200));
  }),
  rest.get('https://api.dev.tucana.sibel.health/web/health', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        status: 'Healthy',
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

describe('SystemStatusBar', () => {
  beforeAll(() => {
    jest.useFakeTimers();
  });

  it('renders error message when server is offline', async () => {
    server.use(
      rest.get('https://api.dev.tucana.sibel.health/web/health', (req, res, ctx) => {
        return res(
          ctx.json({
            status: 'Error',
          })
        );
      })
    );

    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <PatientsContext>
            <SystemStatusBar />
          </PatientsContext>
        </SessionContext>
      </QueryClientProvider>
    );

    await waitFor(
      () => {
        expect(screen.getByText('Data Error')).toBeInTheDocument();
      },
      { timeout: 5000 }
    ); // timeout needed for 3 retires
  });

  it('renders date and time based on env var TZ', async () => {
    render(
      <RuntimeConfigProvider>
        <QueryClientProvider client={queryClient}>
          <SessionContext>
            <PatientsContext>
              <SystemStatusBar />
            </PatientsContext>
          </SessionContext>
        </QueryClientProvider>
      </RuntimeConfigProvider>
    );

    expect(
      screen.getByText(
        `${moment().tz('UTC').format('yyyy-MM-DD')} | ${moment().tz('UTC').format('HH:mm')}`
      )
    ).toBeInTheDocument();

    expect(
      screen.queryByText('Not all groups are displaying on the monitors.')
    ).not.toBeInTheDocument();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.8.1.15
   */
  it('renders hospital name based on env var TITLE', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <RuntimeConfigProvider>
          <SessionContext>
            <PatientsContext>
              <SystemStatusBar />
            </PatientsContext>
          </SessionContext>
        </RuntimeConfigProvider>
      </QueryClientProvider>
    );
    // eslint-disable-next-line
    expect(screen.getByText("Children's Hospital")).toBeInTheDocument();
  });

  it('renders error message when network is offline', async () => {
    Object.defineProperty(window.navigator, 'onLine', {
      value: false,
      configurable: true,
    });
    const goOffline = new window.Event('offline');

    render(
      <QueryClientProvider client={queryClient}>
        <RuntimeConfigProvider>
          <SessionContext>
            <PatientsContext>
              <SystemStatusBar />
            </PatientsContext>
          </SessionContext>
        </RuntimeConfigProvider>
      </QueryClientProvider>
    );

    window.dispatchEvent(goOffline);
    jest.advanceTimersByTime(2000);
    await waitFor(
      () => {
        // eslint-disable-next-line
        expect(screen.getByText('No network available')).toBeInTheDocument();
      },
      { timeout: 500 }
    );
  });

  it('updates time every minute', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <RuntimeConfigProvider>
          <SessionContext>
            <PatientsContext>
              <SystemStatusBar />
            </PatientsContext>
          </SessionContext>
        </RuntimeConfigProvider>
      </QueryClientProvider>
    );

    expect(
      screen.getByText(
        `${moment().tz('UTC').format('yyyy-MM-DD')} | ${moment().tz('UTC').format('HH:mm')}`
      )
    ).toBeInTheDocument();
    jest.advanceTimersByTime(20000 * 4);
    await waitFor(() => {
      expect(
        screen.getByText(
          `${moment().tz('UTC').format('yyyy-MM-DD')} | ${moment().tz('UTC').format('HH:mm')}`
        )
      ).toBeInTheDocument();
    });
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.5.2.1
   */
  it('renders monitor IDs', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <PatientsContext>
            <SystemStatusBar />
          </PatientsContext>
        </SessionContext>
      </QueryClientProvider>
    );

    expect(
      screen.getByText(
        'Not all patient monitors are displayed. Please check group management settings.'
      )
    ).toBeInTheDocument();
  });
});
