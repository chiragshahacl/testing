import PatientsContext from '@/context/PatientsContext';
import SessionContext from '@/context/SessionContext';
import { MockPatientMonitors, ServerSideMockBeds } from '@/utils/groupsMockData';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import TestComponent from '../__mocks__/PatientContextChild';

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
      ctx.status(200),
      ctx.json({
        resources: ServerSideMockBeds,
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
  }),
  rest.get('/web/bed-group', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        resources: [],
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('PatientsContext', () => {
  it('getActiveGroup > empty group', async () => {
    server.use(
      rest.get('/web/bed-group', (req, res, ctx) => {
        return res(
          ctx.status(200),
          ctx.json({
            resources: [],
          })
        );
      })
    );

    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <PatientsContext>
            <TestComponent />
          </PatientsContext>
        </SessionContext>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/groups count: 0/)).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: 'getActiveGroup' }));
    await waitFor(() => {
      expect(screen.getByText('activeGroup: {"id":"","name":"","beds":[]}')).toBeInTheDocument();
    });
  });

  it('getActiveGroup > no data', async () => {
    server.use(
      rest.get('/web/bed-group', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <PatientsContext>
            <TestComponent />
          </PatientsContext>
        </SessionContext>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/groups count: 0/)).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: 'getActiveGroup' }));
    await waitFor(() => {
      expect(screen.getByText('activeGroup: {"id":"","name":"","beds":[]}')).toBeInTheDocument();
    });
  });
});
