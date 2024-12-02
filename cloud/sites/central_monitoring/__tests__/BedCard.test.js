import { ThemeProvider } from '@mui/material';
import { fireEvent, render, screen } from '@testing-library/react';

import theme from '@/theme/theme';

import BedCard from '@/components/cards/BedCard';
import { ERROR_VALUE } from '@/constants';
import PatientsContext, { PatientsData } from '@/context/PatientsContext';
import SessionContext from '@/context/SessionContext';
import { SENSOR_TYPES } from '@/types/sensor';
import { ALERT_PRIORITY, ALERT_TYPES, DEVICE_ALERT_CODES, DEVICE_CODES } from '@/utils/metricCodes';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { alertThresholdsMock, metricsMock } from '../__mocks__/bedCardMocks';
import { EncounterStatus } from '@/types/encounters';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 0,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
    },
  },
});

describe('BedCard', () => {
  it('renders all components', async () => {
    render(
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <SessionContext>
            <PatientsContext>
              <BedCard
                title='Bed 001'
                patientPrimaryIdentifier='PT-001'
                bedId='B-001'
                sendUpdateCallback={jest.fn()}
                metrics={metricsMock}
                alertThresholds={alertThresholdsMock}
                activeSensors={[
                  {
                    id: 'id',
                    type: 'HR',
                  },
                  {
                    id: 'id',
                    type: 'SPO',
                  },
                ]}
                encounterStatus={EncounterStatus.IN_PROGRESS}
              />
            </PatientsContext>
          </SessionContext>
        </QueryClientProvider>
      </ThemeProvider>
    );

    expect(screen.getByText('Bed ID Bed 001')).toBeInTheDocument();
    expect(screen.queryByTestId('device-alerts')).not.toBeInTheDocument();
    expect(screen.queryByTestId('vitals-alerts')).not.toBeInTheDocument();
    expect(screen.getByText('HR')).toBeInTheDocument();
    expect(screen.getByText('SPO2')).toBeInTheDocument();
    expect(screen.queryByText('LOADING...')).not.toBeInTheDocument();
    expect(screen.queryByText('NOT AVAILABLE')).not.toBeInTheDocument();
  });

  it('highlights selected bed', async () => {
    render(
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <SessionContext>
            <PatientsData.Provider
              value={{
                selectedBed: {
                  id: 'B-001',
                  bedNo: 'B-001',
                },
                updateSelectedBed: jest.fn(),
                loadingSelectedBed: false,
              }}
            >
              <BedCard
                title='Bed 001'
                patientPrimaryIdentifier='PT-001'
                bedId='B-001'
                sendUpdateCallback={jest.fn()}
                metrics={metricsMock}
                alertThresholds={alertThresholdsMock}
                activeSensors={[
                  {
                    id: 'id',
                    type: SENSOR_TYPES.ADAM,
                  },
                  {
                    id: 'id1',
                    type: SENSOR_TYPES.LIMB,
                  },
                ]}
                encounterStatus={EncounterStatus.IN_PROGRESS}
              />
            </PatientsData.Provider>
          </SessionContext>
        </QueryClientProvider>
      </ThemeProvider>
    );

    expect(screen.getByTestId('bed-card')).toHaveStyle({ border: '2px solid #FFFFFF' });
  });

  it('updates selected bed on click', async () => {
    const updateSelectedBedMock = jest.fn();

    render(
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <SessionContext>
            <PatientsData.Provider
              value={{
                selectedBed: {
                  id: 'B-002',
                  bedNo: 'B-002',
                },
                updateSelectedBed: updateSelectedBedMock,
                loadingSelectedBed: false,
              }}
            >
              <BedCard
                title='Bed 001'
                patientPrimaryIdentifier='PT-001'
                bedId='B-001'
                sendUpdateCallback={jest.fn()}
                metrics={metricsMock}
                alertThresholds={alertThresholdsMock}
                activeSensors={[
                  {
                    id: 'id',
                    type: SENSOR_TYPES.ADAM,
                  },
                  {
                    id: 'id1',
                    type: SENSOR_TYPES.LIMB,
                  },
                ]}
                encounterStatus={EncounterStatus.IN_PROGRESS}
              />
            </PatientsData.Provider>
          </SessionContext>
        </QueryClientProvider>
      </ThemeProvider>
    );

    fireEvent.click(screen.getByTestId('bed-card'));
    expect(updateSelectedBedMock).toHaveBeenCalledWith('B-001');
  });

  it('indicates loading HR and SPO values', async () => {
    render(
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <SessionContext>
            <PatientsData.Provider
              value={{
                selectedBed: {
                  id: 'B-001',
                  bedNo: 'B-001',
                },
                updateSelectedBed: jest.fn(),
                loadingSelectedBed: true,
              }}
            >
              <BedCard
                title='Bed 001'
                patientPrimaryIdentifier='PT-001'
                bedId='B-001'
                sendUpdateCallback={jest.fn()}
                metrics={metricsMock}
                alertThresholds={alertThresholdsMock}
                activeSensors={[
                  {
                    id: 'id',
                    type: SENSOR_TYPES.ADAM,
                  },
                  {
                    id: 'id1',
                    type: SENSOR_TYPES.LIMB,
                  },
                ]}
                encounterStatus={EncounterStatus.IN_PROGRESS}
              />
            </PatientsData.Provider>
          </SessionContext>
        </QueryClientProvider>
      </ThemeProvider>
    );

    expect(screen.getByText('LOADING...')).toBeInTheDocument();
  });

  it('displays unacknowledged vitals alert -> high priority', async () => {
    const MockVitalAlerts = [
      {
        id: 'DA-001',
        code: '30013',
        deviceId: '40000',
        priority: ALERT_PRIORITY.HIGH,
      },
      {
        id: 'DA-002',
        code: '30014',
        deviceId: '40000',
        priority: ALERT_PRIORITY.MEDIUM,
      },
    ];

    render(
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <SessionContext>
            <PatientsContext>
              <BedCard
                title='Bed 001'
                patientPrimaryIdentifier='PT-001'
                bedId='B-001'
                alerts={MockVitalAlerts}
                metrics={metricsMock}
                alertThresholds={alertThresholdsMock}
                activeSensors={[
                  {
                    id: 'id',
                    type: SENSOR_TYPES.ADAM,
                  },
                  {
                    id: 'id1',
                    type: SENSOR_TYPES.LIMB,
                  },
                ]}
                encounterStatus={EncounterStatus.IN_PROGRESS}
              />
            </PatientsContext>
          </SessionContext>
        </QueryClientProvider>
      </ThemeProvider>
    );

    expect(screen.getByTestId('device-alerts')).toBeInTheDocument();
    expect(screen.getByTestId('device-alerts')).toContainElement(screen.getByText('2'));
    fireEvent.click(screen.getByTestId('device-alerts'));
    expect(screen.getByTestId('device-alerts')).toHaveStyle('backgroundColor: #FF4C42');
  });

  it('displays unacknowledged vitals alert -> medium priority', async () => {
    const MockVitalAlerts = [
      {
        id: 'DA-001',
        code: '30013',
        deviceId: '40000',
        priority: ALERT_PRIORITY.LOW,
      },
      {
        id: 'DA-002',
        code: '30014',
        deviceId: '40000',
        priority: ALERT_PRIORITY.MEDIUM,
      },
    ];

    render(
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <SessionContext>
            <PatientsContext>
              <BedCard
                title='Bed 001'
                patientPrimaryIdentifier='PT-001'
                bedId='B-001'
                alerts={MockVitalAlerts}
                metrics={metricsMock}
                alertThresholds={alertThresholdsMock}
                activeSensors={[
                  {
                    id: 'id',
                    type: SENSOR_TYPES.ADAM,
                  },
                  {
                    id: 'id1',
                    type: SENSOR_TYPES.LIMB,
                  },
                ]}
                encounterStatus={EncounterStatus.IN_PROGRESS}
              />
            </PatientsContext>
          </SessionContext>
        </QueryClientProvider>
      </ThemeProvider>
    );

    expect(screen.getByTestId('device-alerts')).toBeInTheDocument();
    expect(screen.getByTestId('device-alerts')).toContainElement(screen.getByText('2'));
    expect(screen.getByTestId('device-alerts')).toHaveStyle('backgroundColor: #F6C905');
  });

  it('displays unacknowledged vitals alert -> low priority', async () => {
    const MockVitalAlerts = [
      {
        id: 'DA-001',
        code: '30013',
        deviceId: '40000',
        priority: ALERT_PRIORITY.LOW,
      },
      {
        id: 'DA-002',
        code: '30014',
        deviceId: '40000',
        priority: ALERT_PRIORITY.LOW,
      },
    ];

    render(
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <SessionContext>
            <PatientsContext>
              <BedCard
                title='Bed 001'
                patientPrimaryIdentifier='PT-001'
                bedId='B-001'
                alerts={MockVitalAlerts}
                metrics={metricsMock}
                alertThresholds={alertThresholdsMock}
                activeSensors={[
                  {
                    id: 'id',
                    type: SENSOR_TYPES.ADAM,
                  },
                  {
                    id: 'id1',
                    type: SENSOR_TYPES.LIMB,
                  },
                ]}
                encounterStatus={EncounterStatus.IN_PROGRESS}
              />
            </PatientsContext>
          </SessionContext>
        </QueryClientProvider>
      </ThemeProvider>
    );

    // eslint-disable-next-line
    expect(screen.getByTestId('bed-card')).toHaveStyle("backgroundColor: '#204160'");
    expect(screen.getByTestId('device-alerts')).toBeInTheDocument();
    expect(screen.getByTestId('device-alerts')).toContainElement(screen.getByText('2'));
    expect(screen.getByTestId('device-alerts')).toHaveStyle({ backgroundColor: '#75F8FC' });
  });

  it('highlights text based on alert', async () => {
    const MockVitalAlerts = [
      {
        type: ALERT_TYPES.VITALS,
        id: 'A-002',
        code: '258054',
        deviceCode: 'ADAM',
        priority: 'HI',
        acknowledged: false,
        timestamp: '2023-07-20T10:26:01.134',
      },
      {
        type: ALERT_TYPES.VITALS,
        id: 'A-001',
        code: '258066',
        deviceCode: 'limb',
        priority: 'ME',
        acknowledged: false,
        timestamp: '2023-07-20T09:26:01.134',
      },
    ];

    render(
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <SessionContext>
            <PatientsContext>
              <BedCard
                title='Bed 001'
                patientPrimaryIdentifier='PT-001'
                bedId='B-001'
                alerts={MockVitalAlerts}
                metrics={metricsMock}
                alertThresholds={alertThresholdsMock}
                activeSensors={[
                  {
                    id: 'id',
                    type: SENSOR_TYPES.ADAM,
                  },
                  {
                    id: 'id1',
                    type: SENSOR_TYPES.LIMB,
                  },
                ]}
                encounterStatus={EncounterStatus.IN_PROGRESS}
              />
            </PatientsContext>
          </SessionContext>
        </QueryClientProvider>
      </ThemeProvider>
    );

    expect(screen.getByText('60')).toHaveStyle({ color: '#F6C905' });
    expect(screen.getByText('98')).toHaveStyle({ color: '#F6C905' });
  });

  it('displays unacknowledged device alert', async () => {
    const mockVitalsAlerts = [
      {
        id: 'A-001',
        type: DEVICE_CODES.ANNE_CHEST.type,
        code: DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code,
        deviceCode: 'ANNE Chest',
      },
      {
        id: 'A-002',
        type: DEVICE_CODES.ADAM.type,
        code: DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code,
        deviceCode: 'ADAM',
      },
    ];

    render(
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <SessionContext>
            <PatientsContext>
              <BedCard
                title='Bed 001'
                patientPrimaryIdentifier='PT-001'
                bedId='B-001'
                alerts={mockVitalsAlerts}
                metrics={metricsMock}
                alertThresholds={alertThresholdsMock}
                activeSensors={[
                  {
                    id: 'id',
                    type: SENSOR_TYPES.ADAM,
                  },
                  {
                    id: 'id1',
                    type: SENSOR_TYPES.LIMB,
                  },
                ]}
                encounterStatus={EncounterStatus.IN_PROGRESS}
              />
            </PatientsContext>
          </SessionContext>
        </QueryClientProvider>
      </ThemeProvider>
    );

    expect(screen.getByTestId('device-alerts')).toBeInTheDocument();
    expect(screen.getByText('-?-')).toBeInTheDocument();
  });

  it('shows error value in presence of technical alert for SPO', async () => {
    const mockVitalsAlerts = [
      {
        id: 'A-002',
        type: DEVICE_CODES.ANNE_CHEST.type,
        code: DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code,
        deviceCode: 'ANNE Chest',
      },
    ];

    render(
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <SessionContext>
            <PatientsContext>
              <BedCard
                title='Bed 001'
                patientPrimaryIdentifier='PT-001'
                bedId='B-001'
                alerts={mockVitalsAlerts}
                metrics={metricsMock}
                alertThresholds={alertThresholdsMock}
                activeSensors={[
                  {
                    id: 'id',
                    type: SENSOR_TYPES.ADAM,
                  },
                  {
                    id: 'id1',
                    type: SENSOR_TYPES.LIMB,
                  },
                ]}
                encounterStatus={EncounterStatus.IN_PROGRESS}
              />
            </PatientsContext>
          </SessionContext>
        </QueryClientProvider>
      </ThemeProvider>
    );

    expect(screen.getByTestId('device-alerts')).toBeInTheDocument();
    expect(screen.getByText('-?-')).toBeInTheDocument();
  });

  it('shows error value in presence of technical alert for HR', async () => {
    const mockVitalsAlerts = [
      {
        id: 'A-001',
        type: DEVICE_CODES.NONIN_3150.type,
        code: DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code,
        deviceCode: 'Nonin 3150',
      },
      {
        id: 'A-002',
        type: DEVICE_CODES.ANNE_CHEST.type,
        code: DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code,
        deviceCode: 'ANNE Chest',
      },
    ];

    render(
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <SessionContext>
            <PatientsContext>
              <BedCard
                title='Bed 001'
                patientPrimaryIdentifier='PT-001'
                bedId='B-001'
                alerts={mockVitalsAlerts}
                metrics={metricsMock}
                alertThresholds={alertThresholdsMock}
                activeSensors={[
                  {
                    id: 'id',
                    type: SENSOR_TYPES.ADAM,
                  },
                  {
                    id: 'id1',
                    type: SENSOR_TYPES.NONIN,
                  },
                ]}
                encounterStatus={EncounterStatus.IN_PROGRESS}
              />
            </PatientsContext>
          </SessionContext>
        </QueryClientProvider>
      </ThemeProvider>
    );

    expect(screen.getByTestId('device-alerts')).toBeInTheDocument();
    const errorValues = screen.getAllByText(ERROR_VALUE);
    expect(errorValues.length).toBe(2); // There are no values for HR nor SPO, so both show the ERROR_VALUE
  });

  /*
   * Reqirement IDs: RQ-00022-B: SR-1.8.1.26
   */
  it('shows patient monitor unavailable alert', async () => {
    const mockDeviceAlerts = [
      {
        id: 'DA-001',
        acknowledged: false,
        code: DEVICE_ALERT_CODES.MONITOR_NOT_AVAILABLE_ALERT.code,
        deviceId: '40006',
        deviceCode: 'Patient Monitor',
        priority: ALERT_PRIORITY.HIGH,
      },
    ];

    render(
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <SessionContext>
            <PatientsContext>
              <BedCard
                title='Bed 001'
                patientPrimaryIdentifier='PT-001'
                bedId='B-001'
                alerts={mockDeviceAlerts}
                metrics={metricsMock}
                alertThresholds={alertThresholdsMock}
                activeSensors={[
                  {
                    id: 'id',
                    type: SENSOR_TYPES.ADAM,
                  },
                  {
                    id: 'id1',
                    type: SENSOR_TYPES.LIMB,
                  },
                ]}
                encounterStatus={EncounterStatus.IN_PROGRESS}
              />
            </PatientsContext>
          </SessionContext>
        </QueryClientProvider>
      </ThemeProvider>
    );

    expect(screen.getByText('NOT AVAILABLE')).toBeInTheDocument();
    expect(screen.getByTestId('device-alerts')).toHaveStyle({ backgroundColor: '#FF4C42' });
  });

  it('shows no patient alert', async () => {
    render(
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <SessionContext>
            <PatientsContext>
              <BedCard
                title='Bed 001'
                patientPrimaryIdentifier='PT-001'
                bedId='B-001'
                sendUpdateCallback={jest.fn()}
                metrics={metricsMock}
                alertThresholds={alertThresholdsMock}
                activeSensors={[
                  {
                    id: 'id',
                    type: 'HR',
                  },
                  {
                    id: 'id',
                    type: 'SPO',
                  },
                ]}
              />
            </PatientsContext>
          </SessionContext>
        </QueryClientProvider>
      </ThemeProvider>
    );

    expect(screen.getByText('SELECT TO ADMIT PATIENT')).toBeInTheDocument();
  });
});
