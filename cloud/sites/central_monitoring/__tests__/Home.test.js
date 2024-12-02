import Home from '@/app/(authenticated)/home/page';
import AudioManagerContext from '@/context/AudioManagerContext';
import MetricsContext from '@/context/MetricsContext';
import PatientsContext from '@/context/PatientsContext';
import SessionContext from '@/context/SessionContext';
import theme from '@/theme/theme';
import { MockBeds, MockGroups, MockPatientMonitors } from '@/utils/groupsMockData';
import { ThemeProvider } from '@mui/material';
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

const server = setupServer(
  rest.post('/web/auth/token', (req, res, ctx) => {
    return res(
      ctx.json({
        access: 'access',
        refresh: 'refresh',
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

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Home', () => {
  beforeAll(() => jest.useFakeTimers());

  /*
   * Requirement IDs: RQ-00022-B: SR-1.2.4.25 RQ-00022-B: SR-1.3.2.1, SR-1.3.1.1, SR-1.5.2.1, SR-1.5.2.3, SR-1.5.2.5, SR-1.5.2.6
   */
  it('renders all components', async () => {
    render(
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <SessionContext>
            <AudioManagerContext>
              <PatientsContext>
                <MetricsContext>
                  <Home />
                </MetricsContext>
              </PatientsContext>
            </AudioManagerContext>
          </SessionContext>
        </QueryClientProvider>
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('active-group-beds').childNodes).toHaveLength(16);
    });

    fireEvent.click(screen.getAllByTestId('graph-card-container')[0]);
    jest.advanceTimersByTime(50);
    await waitFor(() => {
      expect(screen.getByTestId('selected-bed')).toBeVisible();
    });
  });
});
