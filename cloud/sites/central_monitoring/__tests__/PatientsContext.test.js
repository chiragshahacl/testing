import PatientsContext from '@/context/PatientsContext';
import SessionContext from '@/context/SessionContext';
import { MockGroups, MockPatientMonitors, ServerSideMockBeds } from '@/utils/groupsMockData';
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
        resources: MockGroups,
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('PatientsContext', () => {
  it('updates selected bed and resets beds', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <PatientsContext>
            <TestComponent />
          </PatientsContext>
        </SessionContext>
      </QueryClientProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: 'updateSelectedBed' }));
    await waitFor(() =>
      expect(
        screen.getByText(
          'fetchedBed: {"id":"bed_3","bedNo":"Bed 3","patient":{"patientId":"00000000-0000-0000-0000-000000000002","patientPrimaryIdentifier":"pid3","patientFirstName":"John","patientLastName":"Doe","patientGender":"Male","patientDob":"04/01/1984"}}'
        )
      ).toBeInTheDocument()
    );
    fireEvent.click(screen.getByRole('button', { name: 'resetPatientsContext' }));
    expect(screen.getByText(/fetchedBed:/)).toBeInTheDocument();
  });

  it('removeSelfFromBedsDisplayGroup', async () => {
    const mockSetItem = jest.spyOn(Storage.prototype, 'setItem');

    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <PatientsContext>
            <TestComponent />
          </PatientsContext>
        </SessionContext>
      </QueryClientProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: 'removeSelfFromBedsDisplayGroup' }));
    expect(mockSetItem).toHaveBeenCalledWith('displayedBeds', '[]');
  });

  it('updateBedsOnDisplay', async () => {
    const mockSetItem = jest.spyOn(Storage.prototype, 'setItem');

    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <PatientsContext>
            <TestComponent />
          </PatientsContext>
        </SessionContext>
      </QueryClientProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: 'updateBedsOnDisplay' }));
    expect(mockSetItem).toHaveBeenCalledWith('displayedBeds', expect.any(String));
  });

  it('updateActiveGroup', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <PatientsContext>
            <TestComponent />
          </PatientsContext>
        </SessionContext>
      </QueryClientProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: 'updateActiveGroup' }));
    await waitFor(() => {
      expect(screen.getByText(/activeGroupId: group_3/)).toBeInTheDocument();
    });
  });

  it('getGroupById', async () => {
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
      expect(screen.getByText(/groups count: 5/)).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: 'getGroupById' }));
    await waitFor(() => {
      expect(
        screen.getByText(
          'fetchedGroup: {"id":"group_4","name":"Group 4","beds":[{"id":"bed_1","patient":{},"encounter":{"createdAt":"12-12-2000 13:00:00","status":"in-progress","startTime":"12-12-2000 13:00:05"}},{"id":"bed_2","patient":{}}]}'
        )
      ).toBeInTheDocument();
    });
  });

  it('selectedBed', async () => {
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
      expect(screen.getByText(/beds count: 16/)).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: 'updateSelectedBed' }));
    await waitFor(() =>
      expect(
        screen.getByText(
          'fetchedBed: {"id":"bed_3","bedNo":"Bed 3","patient":{"patientId":"00000000-0000-0000-0000-000000000002","patientPrimaryIdentifier":"pid3","patientFirstName":"John","patientLastName":"Doe","patientGender":"Male","patientDob":"04/01/1984"}}'
        )
      ).toBeInTheDocument()
    );
  });

  it('getActiveGroup > first group', async () => {
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
      expect(screen.getByText(/groups count: 5/)).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: 'resetPatientsContext' }));
    fireEvent.click(screen.getByRole('button', { name: 'getActiveGroup' }));
    await waitFor(() => {
      expect(
        screen.getByText(
          'activeGroup: {"id":"group_1","name":"Group 1","beds":[{"id":"bed_1","patient":{},"encounter":{"createdAt":"12-12-2000 13:00:00","status":"in-progress","startTime":"12-12-2000 13:00:05"}},{"id":"bed_2","patient":{}},{"id":"bed_3","patient":{}},{"id":"bed_4","patient":{}},{"id":"bed_5","patient":{}},{"id":"bed_6","patient":{}},{"id":"bed_7","patient":{}},{"id":"bed_8","patient":{}},{"id":"bed_9","patient":{}},{"id":"bed_10","patient":{}},{"id":"bed_11","patient":{}},{"id":"bed_12","patient":{}},{"id":"bed_13","patient":{}},{"id":"bed_14","patient":{}},{"id":"bed_15","patient":{}},{"id":"bed_16","patient":{}}]}'
        )
      ).toBeInTheDocument();
    });
  });

  it('getActiveGroup > current active group', async () => {
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
      expect(screen.getByText(/groups count: 5/)).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: 'updateSelectedBed' }));
    await waitFor(() =>
      expect(
        screen.getByText(
          'fetchedBed: {"id":"bed_3","bedNo":"Bed 3","patient":{"patientId":"00000000-0000-0000-0000-000000000002","patientPrimaryIdentifier":"pid3","patientFirstName":"John","patientLastName":"Doe","patientGender":"Male","patientDob":"04/01/1984"}}'
        )
      ).toBeInTheDocument()
    );
    fireEvent.click(screen.getByRole('button', { name: 'getActiveGroup' }));
    await waitFor(() => {
      expect(
        screen.getByText(
          'activeGroup: {"id":"group_1","name":"Group 1","beds":[{"id":"bed_1","patient":{},"encounter":{"createdAt":"12-12-2000 13:00:00","status":"in-progress","startTime":"12-12-2000 13:00:05"}},{"id":"bed_2","patient":{}},{"id":"bed_3","patient":{}},{"id":"bed_4","patient":{}},{"id":"bed_5","patient":{}},{"id":"bed_6","patient":{}},{"id":"bed_7","patient":{}},{"id":"bed_8","patient":{}},{"id":"bed_9","patient":{}},{"id":"bed_10","patient":{}},{"id":"bed_11","patient":{}},{"id":"bed_12","patient":{}},{"id":"bed_13","patient":{}},{"id":"bed_14","patient":{}},{"id":"bed_15","patient":{}},{"id":"bed_16","patient":{}}]}'
        )
      ).toBeInTheDocument();
    });
  });
});
