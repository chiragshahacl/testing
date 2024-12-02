import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { setupServer } from 'msw/node';
import { rest } from 'msw';

import EHRView from '@/app/(authenticated)/home/details/EHR/EHRView';
import { EHRStep } from '@/utils/ehr';
import { EncounterStatus } from '@/types/encounters';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const mockEmptyBed = {
  id: 'bedId',
  monitorId: 'monitorId',
  bedNo: 'bedNo',
};

const mockSubmittedEncounterBed = {
  id: 'bedId',
  monitorId: 'monitorId',
  bedNo: 'bedNo',
  patient: {
    patientId: 'patientId',
    patientPrimaryIdentifier: 'patientPrimaryIdentifier',
    patientFirstName: 'firstName',
    patientLastName: 'lastName',
    patientGender: 'male',
    patientDob: '12-12-2000',
  },
  encounter: {
    patientId: 'patientId',
    patientMonitorId: 'monitorId',
    createdAt: '1-1-2024 13:00:13',
    status: EncounterStatus.PLANNED,
    startTime: null,
    endTime: null,
  },
};

const mockRejectedSubmissionEncounterBed = {
  id: 'bedId',
  monitorId: 'monitorId',
  bedNo: 'bedNo',
  patient: {
    patientId: 'patientId',
    patientPrimaryIdentifier: 'patientPrimaryIdentifier',
    patientFirstName: 'firstName',
    patientLastName: 'lastName',
    patientGender: 'male',
    patientDob: '12-12-2000',
  },
  encounter: {
    patientId: 'patientId',
    patientMonitorId: 'monitorId',
    createdAt: '1-1-2024 13:00:13',
    status: EncounterStatus.CANCELLED,
    startTime: null,
    endTime: null,
  },
};

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 0,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
    },
  },
});

describe('EHRView', () => {
  const server = setupServer(
    rest.delete('/web/patient/patientId/admission', (req, res, ctx) => {
      return res(ctx.status(204));
    })
  );

  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  it('shows complete admit selection screen when there is no encounter', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <EHRView
          selectedBed={mockEmptyBed}
          currentStep={EHRStep.UNASSIGNED}
          setCurrentStep={() => {}}
        />
      </QueryClientProvider>
    );

    await waitFor(
      () => {
        expect(screen.getByText('Admit and Monitor Patient')).toBeInTheDocument();
      },
      { timeout: 500 }
    );
    expect(screen.getByText('Search')).toBeInTheDocument();
    expect(screen.getByText('Quick Admit New Patient - Anne One')).toBeInTheDocument();
    expect(screen.getByText('Quick admit')).toBeInTheDocument();
  });

  it('shows request submitted screen when there is a submitted encounter', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <EHRView
          selectedBed={mockSubmittedEncounterBed}
          currentStep={EHRStep.SUBMITTED}
          setCurrentStep={() => {}}
        />
      </QueryClientProvider>
    );

    await waitFor(
      () => {
        expect(screen.getByText('Confirm Patient Information')).toBeInTheDocument();
      },
      { timeout: 500 }
    );
    expect(screen.getByText('Admission Request Sent: 2024-01-01 13:00')).toBeInTheDocument();
    expect(
      screen.getByText('Patient information need to be confirmed through patient monitor.')
    ).toBeInTheDocument();
  });

  it('shows rejected submission modal when there is a rejected encounter - successful acknowledgement', async () => {
    const setCurrentStepMock = jest.fn();
    render(
      <QueryClientProvider client={queryClient}>
        <EHRView
          selectedBed={mockRejectedSubmissionEncounterBed}
          currentStep={EHRStep.SUBMITTED}
          setCurrentStep={setCurrentStepMock}
        />
      </QueryClientProvider>
    );

    const spy = jest.spyOn(queryClient, 'invalidateQueries');

    await waitFor(
      () => {
        expect(screen.getByText('Admission Rejected')).toBeInTheDocument();
      },
      { timeout: 500 }
    );
    expect(
      screen.getByText('The admission request was rejected at the bedside patient monitor.')
    ).toBeInTheDocument();
    expect(screen.getByText('Back to admit')).toBeInTheDocument();

    fireEvent.click(screen.getByText('Back to admit'));

    await waitFor(() => {
      expect(spy).toBeCalledWith(['bed']);
      expect(setCurrentStepMock).toBeCalledWith(EHRStep.UNASSIGNED);
    });
  });
});
