import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';

import BedManagementModal from '@/components/modals/BedManagementModal';

import { useBeds } from '@/api/useBeds';
import { usePatientMonitors } from '@/api/usePatientMonitors';
import SessionContext from '@/context/SessionContext';
import { MockBeds, MockPatientMonitorsFE } from '@/utils/groupsMockData';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { get } from 'lodash';
import { translationFile } from '@/utils/translation';

const mockTranslationFile = translationFile;
const mockLodashGet = get;

jest.mock('react-i18next', () => ({
  useTranslation: () => {
    return {
      t: (key, replaceValues) => {
        let translatedText = mockLodashGet(mockTranslationFile['en']['translation'], key, '');
        if (replaceValues && translatedText) {
          Object.entries(replaceValues).forEach(([key, value]) => {
            translatedText = translatedText.replaceAll(`{{${key}}}`, value);
          });
        }
        return translatedText || key;
      },
    };
  },
}));

const mockUsePatientMonitors = usePatientMonitors;
jest.mock('@/api/usePatientMonitors');

const mockUseBeds = useBeds;
jest.mock('@/api/useBeds');

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
    MAX_NUMBER_BEDS: 64,
  }),
}));

const server = setupServer(
  rest.put('https://api.dev.tucana.sibel.health/web/bed/batch', (req, res, ctx) => {
    return res(ctx.status(200));
  }),
  rest.delete('https://api.dev.tucana.sibel.health/web/bed/batch', (req, res, ctx) => {
    return res(ctx.status(200));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('BedManagementModal', () => {
  it('handles finish set up', async () => {
    mockUsePatientMonitors.mockImplementation(() => ({
      data: [
        {
          id: '001',
          monitorId: 'M-001',
          assignedBedId: null,
        },
      ],
      refetch: jest.fn().mockResolvedValue([
        {
          id: '001',
          monitorId: 'M-001',
          assignedBedId: null,
        },
      ]),
    }));

    const bedsMockValue = [
      {
        id: 'b-001',
        monitorId: '',
        bedNo: '1',
        patient: {
          patientId: 'p-001',
          patientPrimaryIdentifier: 'pid1',
          patientFirstName: 'John',
          patientLastName: 'Doe',
          patientGender: 'male',
          patientDob: '01-01-1990',
        },
      },
      {
        id: 'b-002',
        monitorId: '',
        bedNo: '2',
        patient: {
          patientId: 'p-002',
          patientPrimaryIdentifier: 'pid2',
          patientFirstName: 'John',
          patientLastName: 'Doe',
          patientGender: 'male',
          patientDob: '01-01-1990',
        },
      },
    ];

    mockUseBeds.mockImplementation(() => ({
      data: bedsMockValue,
      refetch: jest.fn().mockResolvedValue(bedsMockValue),
      isPlaceholderData: false,
      isSuccess: true,
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <BedManagementModal isOpen onClose={jest.fn()} />
      </QueryClientProvider>
    );

    await waitFor(
      () => {
        expect(screen.getByText(/Step 2/)).toBeInTheDocument();
        expect(screen.getByTestId('finish-bed-setup')).toBeDisabled();
        expect(screen.getByText('N/A')).toBeInTheDocument();
      },
      { timeout: 500 }
    );

    fireEvent.mouseDown(screen.getByText('N/A'));
    fireEvent.click(screen.getByRole('option', { name: '1' }));

    await waitFor(() => {
      expect(screen.getByTestId('finish-bed-setup')).not.toBeDisabled();
    });

    fireEvent.click(screen.getByTestId('finish-bed-setup'));
  });

  it('renders all components', async () => {
    mockUseBeds.mockImplementation(() => ({}));
    mockUsePatientMonitors.mockImplementation(() => ({ data: [] }));

    render(
      <QueryClientProvider client={queryClient}>
        <BedManagementModal isOpen onClose={jest.fn()} />
      </QueryClientProvider>
    );

    await waitFor(
      () => {
        expect(screen.getByText('Bed Management')).toBeInTheDocument();
      },
      { timeout: 500 }
    );
    expect(screen.getByText('Step 1. Add beds to the system (0)')).toBeInTheDocument();
    expect(screen.getByText('Add beds and assign ID to each bed.')).toBeInTheDocument();
    expect(screen.getByTestId('next-assign-beds')).toBeInTheDocument();
  });

  it('handles modal dismiss', async () => {
    const onClose = jest.fn();

    mockUsePatientMonitors.mockImplementation(() => ({ data: [] }));
    mockUseBeds.mockImplementation(() => ({
      data: [{ id: 'id', monitorId: 'monitorId', bedNo: 'Bed 1' }],
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <BedManagementModal isOpen onClose={onClose} />
      </QueryClientProvider>
    );

    await waitFor(
      () => {
        expect(screen.getByTestId('dismiss-modal')).toBeInTheDocument();
      },
      { timeout: 500 }
    );
    fireEvent.click(screen.getByTestId('dismiss-modal'));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.2.2.13
   */
  it('handles maximum bed capacity', async () => {
    mockUseBeds.mockImplementation(() => ({
      data: [...MockBeds, ...MockBeds, ...MockBeds, ...MockBeds],
      refetch: jest.fn(),
    }));

    mockUsePatientMonitors.mockImplementation(() => ({
      data: MockPatientMonitorsFE,
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <BedManagementModal isOpen onClose={jest.fn()} initialStep={1} />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('next-assign-beds')).toBeInTheDocument();
    });

    waitFor(() => {
      expect(screen.getByTestId('add-bed')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('add-bed'));
    waitFor(() => {
      expect(screen.getByText('Bed limit reached')).toBeInTheDocument();
    });
  });

  it('handles bed add', async () => {
    mockUseBeds.mockImplementation(() => ({ data: [], refetch: jest.fn() }));

    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <BedManagementModal isOpen onClose={jest.fn()} />
      </QueryClientProvider>
    );

    expect(screen.getByText('Bed Management')).toBeInTheDocument();
    expect(screen.getByTestId('next-assign-beds')).toBeDisabled();

    waitFor(() => {
      expect(screen.getByTestId('add-bed')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('add-bed'));
    waitFor(() => {
      fireEvent.change(screen.getByTestId('bed-edit-1'), {
        target: { value: 'bed' },
      });
      fireEvent.blur(screen.getByTestId('bed-edit-1'));
    });

    waitFor(() => {
      expect(screen.getByTestId('next-assign-beds')).not.toBeDisabled();
    });

    fireEvent.click(screen.getByTestId('next-assign-beds'));
    waitFor(() => {
      expect(screen.getByText('Step 2. Assign patient monitors to beds')).toBeInTheDocument();
      expect(screen.getByText('Select the bed ID in the second column.')).toBeInTheDocument();
    });
  });

  it('cancel bed add', async () => {
    mockUseBeds.mockImplementation(() => ({ data: [] }));

    mockUsePatientMonitors.mockImplementation(() => ({
      data: [
        {
          id: 'PM-001',
          monitorId: 'PM-ID-001',
        },
      ],
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <BedManagementModal isOpen onClose={jest.fn()} />
      </QueryClientProvider>
    );

    expect(screen.getByTestId('add-bed')).toBeInTheDocument();
    fireEvent.click(screen.getByTestId('add-bed'));

    waitFor(() => {
      expect(screen.getByTestId('bed-edit-1')).toBeInTheDocument();
      expect(screen.getByTestId('remove-bed-1')).toBeInTheDocument();
      fireEvent.click(screen.getByTestId('remove-bed-1'));
    });
    expect(screen.getByText('Step 1. Add beds to the system (0)')).toBeInTheDocument();
  });

  it('handles bed delete', async () => {
    mockUseBeds.mockImplementation(() => ({
      data: MockBeds,
      refetch: jest.fn().mockResolvedValue(MockBeds),
    }));

    mockUsePatientMonitors.mockImplementation(() => ({
      data: [
        {
          id: 'PM-001',
          monitorId: 'PM-ID-001',
          assignedBedId: null,
        },
      ],
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <BedManagementModal isOpen initialStep={1} onClose={jest.fn()} />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Step 1. Add beds to the system (16)')).toBeInTheDocument();
    });
    expect(screen.getByLabelText('Bed 1')).toBeInTheDocument();
    fireEvent.click(screen.getByTestId('remove-bed-1'));
    expect(screen.queryByRole('textbox', { name: 'Bed 1' })).not.toBeInTheDocument();
    expect(screen.getByText('Step 1. Add beds to the system (15)')).toBeInTheDocument();

    fireEvent.click(screen.getByTestId('next-assign-beds'));
    await waitFor(() => {
      expect(screen.getByText('Step 2. Assign patient monitors to beds')).toBeInTheDocument();
      fireEvent.mouseDown(screen.getByText('N/A'));
    });
    expect(screen.queryByRole('option', { name: 'Bed 1' })).not.toBeInTheDocument();
  });

  it('remove bed', async () => {
    const requestSpy = jest.fn();
    server.events.on('request:start', requestSpy);

    mockUseBeds.mockImplementation(() => ({ data: MockBeds, refetch: jest.fn() }));
    mockUsePatientMonitors.mockImplementation(() => ({
      data: [
        {
          id: 'PM-001',
          monitorId: 'PM-ID-001',
        },
      ],
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <BedManagementModal isOpen initialStep={1} onClose={jest.fn()} />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Step 1. Add beds to the system (16)')).toBeInTheDocument();
      expect(screen.getByTestId('remove-bed-1')).toBeInTheDocument();
    });

    act(() => {
      fireEvent.click(screen.getByTestId('remove-bed-1'));
    });

    expect(screen.getByText('Step 1. Add beds to the system (15)')).toBeInTheDocument();
    expect(screen.getByTestId('next-assign-beds')).not.toBeDisabled();

    act(() => {
      fireEvent.click(screen.getByTestId('next-assign-beds'));
    });
    waitFor(
      () => {
        expect(requestSpy).toHaveBeenCalledWith(
          expect.objectContaining({
            method: 'DELETE',
            url: new URL('https://api.dev.tucana.sibel.health/web/bed/batch'),
          })
        );
      },
      { timeout: 100 }
    );
  });

  it('edit bed', async () => {
    mockUsePatientMonitors.mockImplementation(() => ({
      data: [
        {
          id: '001',
          monitorId: 'M-001',
          assignedBedId: null,
        },
        {
          id: '002',
          monitorId: 'M-002',
          assignedBedId: 'b-001',
        },
      ],
    }));

    const bedsMockValue = [
      {
        id: 'b-001',
        monitorId: '',
        bedNo: 'Bed 1',
        patient: {
          patientId: 'p-001',
          patientPrimaryIdentifier: 'pid1',
          patientFirstName: 'John',
          patientLastName: 'Doe',
          patientGender: 'male',
          patientDob: '01-01-1990',
        },
      },
      {
        id: 'b-002',
        monitorId: '',
        bedNo: '2',
        patient: {
          patientId: 'p-002',
          patientPrimaryIdentifier: 'pid2',
          patientFirstName: 'John',
          patientLastName: 'Doe',
          patientGender: 'male',
          patientDob: '01-01-1990',
        },
      },
    ];

    mockUseBeds.mockImplementation(() => ({
      data: bedsMockValue,
      refetch: jest.fn().mockResolvedValue(true),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <BedManagementModal isOpen initialStep={1} onClose={jest.fn()} />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByLabelText('Bed 1')).toBeInTheDocument();
    });
    fireEvent.change(screen.getByLabelText('Bed 1'), {
      target: { value: 'bed 1' },
    });
    fireEvent.blur(screen.getByLabelText('Bed 1'));
    await waitFor(() => {
      expect(screen.getByLabelText('bed 1')).toBeInTheDocument();
      expect(screen.queryByLabelText('Bed 1')).not.toBeInTheDocument();
    });
  });

  it('edit bed -> valid bed number', async () => {
    const requestSpy = jest.fn();
    server.events.on('request:start', requestSpy);

    mockUseBeds.mockImplementation(() => ({
      data: [],
      refetch: jest.fn().mockResolvedValue(true),
    }));

    mockUsePatientMonitors.mockImplementation(() => ({
      data: [
        {
          id: 'PM-001',
          monitorId: 'PM-ID-001',
        },
      ],
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <BedManagementModal isOpen onClose={jest.fn()} />
        </SessionContext>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('add-bed')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('add-bed'));

    await waitFor(() => {
      fireEvent.change(screen.getByTestId('bed-edit-1'), {
        target: { value: 'bed' },
      });
      fireEvent.blur(screen.getByTestId('bed-edit-1'));
    });

    await waitFor(() => {
      expect(screen.getByText('Step 1. Add beds to the system (1)')).toBeInTheDocument();
    });
    fireEvent.change(screen.getByLabelText('bed'), {
      target: { value: 'bed 1' },
    });
    fireEvent.blur(screen.getByLabelText('bed'));
    await waitFor(() => {
      expect(screen.getByLabelText('bed 1')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('next-assign-beds'));
    await waitFor(() => {
      expect(requestSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          method: 'PUT',
          url: new URL('https://api.dev.tucana.sibel.health/web/bed/batch'),
        })
      );
      expect(requestSpy).not.toHaveBeenCalledWith(
        expect.objectContaining({
          method: 'DELETE',
          url: new URL('https://api.dev.tucana.sibel.health/web/bed/batch'),
        })
      );
    });
  });

  it('edit bed -> already used bed number', async () => {
    mockUseBeds.mockImplementation(() => ({ data: [] }));

    mockUsePatientMonitors.mockImplementation(() => ({
      data: [
        {
          id: 'PM-001',
          monitorId: 'PM-ID-001',
        },
      ],
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <BedManagementModal isOpen onClose={jest.fn()} />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('add-bed')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('add-bed'));
    await waitFor(() => {
      fireEvent.change(screen.getByTestId('bed-edit-1'), {
        target: { value: 'bed 1' },
      });
      fireEvent.blur(screen.getByTestId('bed-edit-1'));
    });

    fireEvent.click(screen.getByTestId('add-bed'));
    await waitFor(() => {
      fireEvent.change(screen.getByTestId('bed-edit-2'), {
        target: { value: 'bed 2' },
      });
      fireEvent.blur(screen.getByTestId('bed-edit-2'));
    });

    fireEvent.click(screen.getByTestId('add-bed'));
    await waitFor(() => {
      fireEvent.change(screen.getByTestId('bed-edit-3'), {
        target: { value: 'bed 3' },
      });
      fireEvent.blur(screen.getByTestId('bed-edit-3'));
    });

    await waitFor(() => {
      expect(screen.getByText('Step 1. Add beds to the system (3)')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('add-bed'));
    await waitFor(() => {
      fireEvent.change(screen.getByTestId('bed-edit-4'), {
        target: { value: 'bed 1' },
      });
      fireEvent.blur(screen.getByTestId('bed-edit-4'));
    });

    fireEvent.click(screen.getByTestId('next-assign-beds'));

    await waitFor(() => {
      expect(screen.getAllByText('Bed ID already exists. Change or enter a new one.')).toHaveLength(
        1
      );
    });
  });

  it('edit bed -> empty bed number', async () => {
    mockUseBeds.mockImplementation(() => ({
      data: [
        {
          id: 'bed_1',
          bedNo: 'Bed 1',
          patient: {
            patientFirstName: 'John',
            patientLastName: 'Doe',
            patientGender: 'Male',
            patientPrimaryIdentifier: 'pid1',
            patientId: '00000000-0000-0000-0000-000000000000',
            patientDob: '15/12/1984',
          },
          monitorId: 'S4RJVEKVR2',
        },
      ],
    }));

    mockUsePatientMonitors.mockImplementation(() => ({
      data: [
        {
          id: 'PM-001',
          monitorId: 'PM-ID-001',
        },
      ],
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <BedManagementModal isOpen initialStep={1} onClose={jest.fn()} />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('add-bed')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('add-bed'));
    fireEvent.change(screen.getByTestId('bed-edit-2'), {
      target: { value: 'bed 2' },
    });
    fireEvent.blur(screen.getByTestId('bed-edit-2'));

    fireEvent.change(screen.getByLabelText('bed 2'), {
      target: { value: '' },
    });
    fireEvent.blur(screen.getByLabelText('bed 2'));

    fireEvent.click(screen.getByTestId('next-assign-beds'));

    await waitFor(() => {
      expect(screen.getByText('Please enter the bed ID.')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('remove-bed-2'));
    await waitFor(() => {
      expect(screen.queryByText('Please enter the bed ID.')).not.toBeInTheDocument();
    });
  });

  it('handles bed monitor association', async () => {
    const onClose = jest.fn();

    mockUsePatientMonitors.mockImplementation(() => ({
      data: [
        {
          id: '001',
          monitorId: 'M-001',
        },
      ],
    }));

    const mockBeds = [
      {
        id: 'b-003',
        monitorId: '',
        bedNo: '3',
        patient: {
          patientId: 'p-001',
          patientPrimaryIdentifier: 'pid1',
          patientFirstName: 'John',
          patientLastName: 'Doe',
          patientGender: 'male',
          patientDob: '01-01-1990',
        },
      },
      {
        id: 'b-002',
        monitorId: '',
        bedNo: '2',
        patient: {
          patientId: 'p-002',
          patientPrimaryIdentifier: 'pid2',
          patientFirstName: 'John',
          patientLastName: 'Doe',
          patientGender: 'male',
          patientDob: '01-01-1990',
        },
      },
    ];

    mockUseBeds.mockImplementation(() => ({
      data: mockBeds,
      refetch: jest.fn().mockResolvedValue(mockBeds),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <BedManagementModal isOpen initialStep={1} onClose={onClose} />
      </QueryClientProvider>
    );

    expect(screen.getByTestId('add-bed')).toBeInTheDocument();
    fireEvent.click(screen.getByTestId('add-bed'));
    await waitFor(() => {
      fireEvent.change(screen.getByTestId('bed-edit-3'), {
        target: { value: '4' },
      });
      fireEvent.blur(screen.getByTestId('bed-edit-3'));
    });
    expect(screen.getByLabelText('4')).toBeInTheDocument();

    fireEvent.click(screen.getByTestId('remove-bed-2'));
    await waitFor(() => {
      expect(screen.queryByLabelText('3')).not.toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('next-assign-beds'));
    await waitFor(() => {
      expect(screen.getByText('M-001')).toBeInTheDocument();
      expect(screen.getByText('N/A')).toBeInTheDocument();
    });
    fireEvent.mouseDown(screen.getByText('N/A'));
    fireEvent.click(screen.getByRole('option', { name: '2' }));

    expect(screen.getByTestId('finish-bed-setup')).not.toBeDisabled();
    fireEvent.click(screen.getByTestId('finish-bed-setup'));
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.8.3.2, SR-1.8.3.3 RQ-00022-B: SR-1.8.3.1, SR-1.8.3.5 RQ-00022-B: SR-1.8.3.2, SR-1.8.3.5 	RQ-00022-B: SR-1.8.3.6
   */
  it('handles unsaved changes -> discard', async () => {
    const onClose = jest.fn();
    mockUsePatientMonitors.mockImplementation(() => ({
      data: [
        {
          id: '001',
          monitorId: 'M-001',
          assignedBedId: null,
        },
      ],
    }));

    const bedsMockValue = [
      {
        id: 'b-001',
        monitorId: '',
        bedNo: '1',
        patient: {
          patientId: 'p-001',
          patientPrimaryIdentifier: 'pid1',
          patientFirstName: 'John',
          patientLastName: 'Doe',
          patientGender: 'male',
          patientDob: '01-01-1990',
        },
      },
      {
        id: 'b-002',
        monitorId: '',
        bedNo: '2',
        patient: {
          patientId: 'p-002',
          patientPrimaryIdentifier: 'pid2',
          patientFirstName: 'John',
          patientLastName: 'Doe',
          patientGender: 'male',
          patientDob: '01-01-1990',
        },
      },
    ];
    mockUseBeds.mockImplementation(() => ({
      data: bedsMockValue,
      refetch: jest.fn().mockResolvedValue(bedsMockValue),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <BedManagementModal isOpen initialStep={1} onClose={onClose} />
        </SessionContext>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('add-bed')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('add-bed'));
    await waitFor(() => {
      fireEvent.change(screen.getByTestId('bed-edit-3'), {
        target: { value: '4' },
      });
      fireEvent.blur(screen.getByTestId('bed-edit-3'));
    });

    fireEvent.click(screen.getByTestId('next-assign-beds'));
    await waitFor(() => {
      expect(screen.getByTestId('finish-bed-setup')).toBeDisabled();
    });

    fireEvent.click(screen.getByTestId('dismiss-modal'));
    await waitFor(() => {
      expect(screen.getByText('Unsaved information')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: 'Discard' }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.8.3.6
   */
  it('handles unsaved changes -> continue edit', async () => {
    const onClose = jest.fn();

    mockUsePatientMonitors.mockImplementation(() => ({
      data: [
        {
          id: '001',
          monitorId: 'M-001',
          assignedBedId: null,
        },
      ],
      refetch: jest.fn().mockResolvedValue([
        {
          id: '001',
          monitorId: 'M-001',
          assignedBedId: null,
        },
      ]),
    }));

    const bedsMockValue = [
      {
        id: 'b-001',
        monitorId: '',
        bedNo: '1',
        patient: {
          patientId: 'p-001',
          patientPrimaryIdentifier: 'pid1',
          patientFirstName: 'John',
          patientLastName: 'Doe',
          patientGender: 'male',
          patientDob: '01-01-1990',
        },
      },
      {
        id: 'b-002',
        monitorId: '',
        bedNo: '2',
        patient: {
          patientId: 'p-002',
          patientPrimaryIdentifier: 'pid2',
          patientFirstName: 'John',
          patientLastName: 'Doe',
          patientGender: 'male',
          patientDob: '01-01-1990',
        },
      },
    ];
    mockUseBeds.mockImplementation(() => ({
      data: bedsMockValue,
      refetch: jest.fn().mockResolvedValue(bedsMockValue),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <BedManagementModal isOpen initialStep={1} onClose={onClose} />
        </SessionContext>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('add-bed')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('add-bed'));
    await waitFor(() => {
      fireEvent.change(screen.getByTestId('bed-edit-3'), {
        target: { value: '10' },
      });
      fireEvent.blur(screen.getByTestId('bed-edit-3'));
    });
    fireEvent.click(screen.getByTestId('next-assign-beds'));
    await waitFor(() => {
      expect(screen.getByTestId('finish-bed-setup')).toBeDisabled();
      expect(screen.getByText('M-001')).toBeInTheDocument();
    });
    fireEvent.mouseDown(screen.getByText('N/A'));
    fireEvent.click(screen.getByRole('option', { name: '10' }));
    fireEvent.click(screen.getByTestId('dismiss-modal'));
    await waitFor(() => {
      expect(screen.getByText('Unsaved information')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: 'Back to edit' }));
    await waitFor(() => {
      expect(screen.queryByText('Unsaved information')).not.toBeInTheDocument();
      expect(screen.getByText('Step 2. Assign patient monitors to beds')).toBeInTheDocument();
    });
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.2.3.18
   */
  it('handles bed not assigned to each monitor -> back to edit', async () => {
    mockUsePatientMonitors.mockImplementation(() => ({
      data: [
        {
          id: '001',
          monitorId: 'M-001',
          assignedBedId: null,
        },
        {
          id: '002',
          monitorId: 'M-002',
          assignedBedId: 'b-001',
        },
      ],
    }));

    const bedsMockValue = [
      {
        id: 'b-001',
        monitorId: '',
        bedNo: '1',
        patient: {
          patientId: 'p-001',
          patientPrimaryIdentifier: 'pid1',
          patientFirstName: 'John',
          patientLastName: 'Doe',
          patientGender: 'male',
          patientDob: '01-01-1990',
        },
      },
      {
        id: 'b-002',
        monitorId: '',
        bedNo: '2',
        patient: {
          patientId: 'p-002',
          patientPrimaryIdentifier: 'pid2',
          patientFirstName: 'John',
          patientLastName: 'Doe',
          patientGender: 'male',
          patientDob: '01-01-1990',
        },
      },
    ];
    mockUseBeds.mockImplementation(() => ({ data: bedsMockValue, refetch: jest.fn() }));

    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <BedManagementModal isOpen initialStep={1} onClose={jest.fn()} />
        </SessionContext>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('next-assign-beds')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('next-assign-beds'));
    await waitFor(() => {
      expect(screen.getByText('N/A')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('finish-bed-setup'));
    await waitFor(() => {
      expect(screen.getByText('Confirmation required')).toBeInTheDocument;
    });
    fireEvent.click(screen.getByRole('button', { name: 'Back to edit' }));

    await waitFor(() => {
      expect(screen.queryByText('Confirmation required')).not.toBeInTheDocument();
      expect(screen.getByText('Step 2. Assign patient monitors to beds')).toBeInTheDocument();
    });
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.2.3.17
   */
  it('handles bed not assigned to each monitor -> Confirm', async () => {
    mockUsePatientMonitors.mockImplementation(() => ({
      data: [
        {
          id: '001',
          monitorId: 'M-001',
          assignedBedId: null,
        },
        {
          id: '002',
          monitorId: 'M-002',
          assignedBedId: 'b-001',
        },
      ],
    }));

    const bedsMockValue = [
      {
        id: 'b-001',
        monitorId: '',
        bedNo: '1',
        patient: {
          patientId: 'p-001',
          patientPrimaryIdentifier: 'pid1',
          patientFirstName: 'John',
          patientLastName: 'Doe',
          patientGender: 'male',
          patientDob: '01-01-1990',
        },
      },
      {
        id: 'b-002',
        monitorId: '',
        bedNo: '2',
        patient: {
          patientId: 'p-002',
          patientPrimaryIdentifier: 'pid2',
          patientFirstName: 'John',
          patientLastName: 'Doe',
          patientGender: 'male',
          patientDob: '01-01-1990',
        },
      },
    ];
    mockUseBeds.mockImplementation(() => ({ data: bedsMockValue, refetch: jest.fn() }));

    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <BedManagementModal isOpen initialStep={1} onClose={jest.fn()} />
        </SessionContext>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('next-assign-beds')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('next-assign-beds'));

    await waitFor(() => {
      expect(screen.getByText('N/A')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('finish-bed-setup'));

    await waitFor(() => {
      expect(screen.getByText('Confirmation required')).toBeInTheDocument;
    });

    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.2.1.6
   */
  it('shows server error when initial load fails', async () => {
    mockUseBeds.mockImplementation(() => ({ isError: true }));
    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
      isPlaceholder: false,
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <BedManagementModal isOpen onClose={jest.fn()} />
      </QueryClientProvider>
    );

    waitFor(() =>
      expect(
        screen.getByText('Failed to display beds. Please try again in a few minutes.')
      ).toBeInTheDocument()
    );
  });

  it('shows server error when failed to fetch monitor ids', async () => {
    mockUsePatientMonitors.mockImplementation(() => ({
      isError: true,
    }));

    mockUseBeds.mockImplementation(() => ({ data: MockBeds, refetch: () => null }));

    render(
      <QueryClientProvider client={queryClient}>
        <BedManagementModal isOpen initialStep={1} onClose={jest.fn()} />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('next-assign-beds')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('next-assign-beds'));

    await waitFor(
      () => {
        expect(
          screen.getByText('Failed to display patient monitors. Please try again in a few minutes.')
        ).toBeInTheDocument();
      },
      { timeout: 500 }
    );
  });

  it('shows server error when failed to refresh beds', async () => {
    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
      isPlaceholder: false,
    }));

    mockUseBeds
      .mockImplementationOnce(() => ({
        data: MockBeds,
        isPlaceholder: false,
      }))
      .mockImplementation(() => ({ isError: true }));

    render(
      <QueryClientProvider client={queryClient}>
        <BedManagementModal isOpen onClose={jest.fn()} />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('next-assign-beds')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('next-assign-beds'));
    await waitFor(() => {
      expect(
        screen.getByText('Failed to display beds. Please try again in a few minutes.')
      ).toBeInTheDocument();
    });
  });

  // it('shows server error when failed to add/edit beds', async () => {
  //   server.use(
  //     rest.put('https://api.dev.tucana.sibel.health/web/bed/batch', (req, res, ctx) => {
  //       return res(ctx.status(422));
  //     }),
  //   );

  //   mockUseBeds.mockImplementation(() => ({ data: [], refetch: jest.fn() }));

  //   mockUsePatientMonitors.mockImplementation(() => ({
  //     data: [
  //       {
  //         id: 'PM-001',
  //         monitorId: 'PM-ID-001',
  //       },
  //     ],
  //   }));

  //   render(
  //     <QueryClientProvider client={queryClient}>
  //       <SessionContext>
  //         <BedManagementModal isOpen onClose={jest.fn()} />
  //       </SessionContext>
  //     </QueryClientProvider>
  //   );

  //   await waitFor(() => {
  //     expect(screen.getByTestId('add-bed')).toBeInTheDocument();
  //   });
  //   fireEvent.click(screen.getByTestId('add-bed'));
  //   fireEvent.change(screen.getByTestId('bed-edit-1'), {
  //     target: { value: 'bed' },
  //   });
  //   fireEvent.blur(screen.getByTestId('bed-edit-1'));

  //   await waitFor(() => {
  //     expect(screen.getByText('Step 1. Add beds to the system (1)')).toBeInTheDocument();
  //   });
  //   await waitFor(() => {
  //     fireEvent.click(screen.getByTestId('next-assign-beds'));
  //   });
  //   await waitFor(() => {
  //     expect(screen.getByText('Failed to modify beds')).toBeInTheDocument();
  //   });
  // });
});
