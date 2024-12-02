import SelectedBed from '@/app/(authenticated)/home/details/SelectedBed';
import AudioManagerContext from '@/context/AudioManagerContext';
import MetricsContext from '@/context/MetricsContext';
import PatientsContext from '@/context/PatientsContext';
import SessionContext from '@/context/SessionContext';
import { MockBeds, MockGroups, MockPatientMonitors } from '@/utils/groupsMockData';
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

describe('SelectedBed', () => {
  it('goes back', async () => {
    const handleBackNavigationMock = jest.fn();
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <AudioManagerContext>
            <PatientsContext>
              <MetricsContext>
                <SelectedBed
                  selectedBed={{
                    id: 'bed_1',
                    bedNo: 'Bed 1',
                    patient: null,
                    monitorId: 'S4RJVEKVR2',
                  }}
                  selectedBedGraphsWithData=''
                  selectedTab=''
                  activeSensors={[]}
                  isLoading={false}
                  alerts={[]}
                  onTabSelected={jest.fn()}
                  sendNewDataSeries={jest.fn()}
                  handleBackNavigation={handleBackNavigationMock}
                />
              </MetricsContext>
            </PatientsContext>
          </AudioManagerContext>
        </SessionContext>
      </QueryClientProvider>
    );

    expect(screen.getByTestId('dismiss-modal')).toBeInTheDocument();
    fireEvent.click(screen.getByTestId('dismiss-modal'));
    expect(handleBackNavigationMock).toHaveBeenCalled();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.8.1.27
   */
  it('handles no patient case', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <AudioManagerContext>
            <PatientsContext>
              <MetricsContext>
                <SelectedBed
                  selectedBed={{
                    id: 'bed_1',
                    bedNo: 'Bed 1',
                    patient: null,
                    monitorId: 'S4RJVEKVR2',
                  }}
                  selectedBedGraphsWithData=''
                  selectedTab=''
                  activeSensors={[]}
                  isLoading={false}
                  alerts={[]}
                  onTabSelected={jest.fn()}
                  sendNewDataSeries={jest.fn()}
                  handleBackNavigation={jest.fn()}
                />
              </MetricsContext>
            </PatientsContext>
          </AudioManagerContext>
        </SessionContext>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Admit and Monitor Patient')).toBeInTheDocument();
    });
  });

  it('gives access to alarm history in Development mode', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <AudioManagerContext>
            <PatientsContext>
              <MetricsContext>
                <SelectedBed
                  selectedBed={MockBeds[0]}
                  selectedBedGraphsWithData=''
                  selectedTab=''
                  activeSensors={[]}
                  isLoading={false}
                  alerts={[]}
                  onTabSelected={jest.fn()}
                  sendNewDataSeries={jest.fn()}
                  handleBackNavigation={jest.fn()}
                />
              </MetricsContext>
            </PatientsContext>
          </AudioManagerContext>
        </SessionContext>
      </QueryClientProvider>
    );

    expect(screen.getByText('VITALS')).toBeInTheDocument();
    expect(screen.getByText('PATIENT INFO')).toBeInTheDocument();
    expect(screen.getByText('ALARM LIMITS')).toBeInTheDocument();
    expect(process.env.NEXT_PUBLIC_ENVIRONMENT).toBe('Development');
    expect(screen.getByText('ALARM HISTORY')).toBeInTheDocument();
  });
});
