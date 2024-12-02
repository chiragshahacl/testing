import { render, screen } from '@testing-library/react';

import GraphCard from '@/components/graph/GraphCard';
import SessionContext from '@/context/SessionContext';

import {
  ALERT_TYPES,
  DEVICE_ALERT_CODES,
  METRIC_INTERNAL_CODES,
  RANGES_CODES,
  VITALS_ALERT_CODES,
} from '@/utils/metricCodes';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 0,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
    },
  },
});

jest.mock('scichart', () => ({
  __esModule: true,
  NumberRange: jest.fn(),
  NumericAxis: jest.fn().mockReturnValue({
    labelProvider: {
      numericFormat: 'Decimal',
    },
  }),
  ENumericFormat: {
    Decimal: 'Decimal',
  },
  EAutoRange: {
    Once: 'Once',
  },
  SciChartSurface: {
    create: () => {
      return {
        sciChartSurface: {
          xAxes: {
            add: jest.fn(),
          },
          yAxes: {
            add: jest.fn(),
          },
          renderableSeries: {
            add: jest.fn(),
          },
        },
        wasmContext: {},
      };
    },
  },
  FastLineRenderableSeries: jest.fn(),
  XyDataSeries: jest.fn().mockImplementation(() => ({
    appendRange: jest.fn(),
  })),
}));

const MockAlertThresholds = {
  [RANGES_CODES.HR]: {
    upperLimit: '120',
    lowerLimit: '45',
  },
};

describe('GraphCard', () => {
  it('renders all components', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <GraphCard
            bedData={{
              id: 'B-001',
              monitorId: 'PM-001',
              bedNo: 'Bed 1',
              patient: {
                patientId: 'P-001',
                patientPrimaryIdentifier: 'p-id-001',
                patientFirstName: 'John',
                patientLastName: 'Doe',
                patientGender: 'male',
                patientDob: '1990-01-01',
              },
            }}
            elementId='E-001'
            metric={METRIC_INTERNAL_CODES.ECG}
            showText={'all'}
            showAlerts={false}
            smallView={false}
            sendUpdateCallback={jest.fn()}
            alertThresholds={MockAlertThresholds}
            metrics={{
              hr: {
                value: 100,
                unit: '264864',
                timestamp: '2023-07-20T09:26:01.134',
              },
            }}
            showSummary
            hasActivePatientSession
          />
        </SessionContext>
      </QueryClientProvider>
    );

    expect(screen.queryByText('ECG')).toBeInTheDocument();
    expect(screen.getByText('Bed ID Bed 1')).toBeInTheDocument();
    expect(screen.getByText('Doe, J.')).toBeInTheDocument();
    expect(screen.getByText('HR (bpm)')).toBeInTheDocument();
    expect(screen.getByText('120')).toBeInTheDocument();
    expect(screen.getByText('45')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument();
  });

  it('hides graph summary when text is hidden', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <GraphCard
            bedData={{
              id: 'B-001',
              monitorId: 'PM-001',
              bedNo: 'Bed 1',
              patient: {
                patientId: 'P-001',
                patientPrimaryIdentifier: 'p-id-001',
                patientFirstName: 'John',
                patientLastName: 'Doe',
                patientGender: 'male',
                patientDob: '1990-01-01',
              },
            }}
            maxHeight='100px'
            elementId='E-001'
            metric={METRIC_INTERNAL_CODES.ECG}
            showText={'bedInfo'}
            showAlerts={false}
            smallView={true}
            sendUpdateCallback={jest.fn()}
            hasActivePatientSession
          />
        </SessionContext>
      </QueryClientProvider>
    );

    expect(screen.queryByText('ECG')).not.toBeInTheDocument();
    expect(screen.queryByText('Bed ID Bed 1')).toBeInTheDocument();
    expect(screen.queryByText('Doe, J.')).toBeInTheDocument();
  });

  it('shows error message instead of chart', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <GraphCard
            bedData={{
              id: 'B-001',
              monitorId: 'PM-001',
              bedNo: 'Bed 1',
              patient: {
                patientId: 'P-001',
                patientPrimaryIdentifier: 'p-id-001',
                patientFirstName: 'John',
                patientLastName: 'Doe',
                patientGender: 'male',
                patientDob: '1990-01-01',
              },
            }}
            maxHeight='100px'
            elementId='E-001'
            metricName='ECG'
            showText={'bedInfo'}
            showAlerts={false}
            smallView={true}
            sendUpdateCallback={jest.fn()}
            hasChestSensorConnected={false}
            hasActivePatientSession
          />
        </SessionContext>
      </QueryClientProvider>
    );

    expect(screen.getByText('NO ANNE CHEST SENSOR PAIRED')).toBeInTheDocument();
  });

  it('shows alert list', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <GraphCard
            bedData={{
              id: 'B-001',
              monitorId: 'PM-001',
              bedNo: 'Bed 1',
              patient: {
                patientId: 'P-001',
                patientPrimaryIdentifier: 'p-id-001',
                patientFirstName: 'John',
                patientLastName: 'Doe',
                patientGender: 'male',
                patientDob: '1990-01-01',
              },
            }}
            maxHeight='100px'
            elementId='E-001'
            metric={METRIC_INTERNAL_CODES.ECG}
            showText={'bedInfo'}
            showAlerts={true}
            smallView={true}
            sendUpdateCallback={jest.fn()}
            alerts={[
              {
                type: ALERT_TYPES.VITALS,
                id: 'A-003',
                code: VITALS_ALERT_CODES.HR_LOW_VISUAL.code,
                deviceId: '40000',
                priority: 'HI',
                acknowledged: false,
                timestamp: '2023-07-20 09:26:48.035001',
              },
              {
                type: ALERT_TYPES.VITALS,
                id: 'A-003',
                code: VITALS_ALERT_CODES.DIA_HIGH_AUDIO.code,
                deviceId: '40000',
                priority: 'LO',
                acknowledged: false,
                timestamp: '2023-07-20T09:26:16.024',
              },
              {
                type: ALERT_TYPES.DEVICE,
                id: 'A-002',
                code: DEVICE_ALERT_CODES.LEAD_OFF_ALERT.code,
                deviceId: 'DC-002',
                priority: 'ME',
                acknowledged: false,
                timestamp: '2023-07-20T11:26:01.134',
              },
              {
                type: ALERT_TYPES.DEVICE,
                id: 'A-002',
                code: DEVICE_ALERT_CODES.LOW_SIGNAL_ALERT.code,
                deviceId: 'DC-002',
                priority: 'ME',
                acknowledged: false,
                timestamp: '2023-07-20T10:26:01.134',
              },
              {
                type: ALERT_TYPES.DEVICE,
                id: 'A-003',
                code: DEVICE_ALERT_CODES.POOR_SKIN_CONTACT_ALERT.code,
                deviceId: 'DC-003',
                priority: 'LO',
                acknowledged: false,
                timestamp: '2023-07-20T10:26:01.134',
              },
            ]}
            showSummary
            metrics={{
              hr: {
                value: 100,
                unit: '264864',
                timestamp: '2023-07-20T14:26:01.134',
              },
            }}
            hasActivePatientSession
          />
        </SessionContext>
      </QueryClientProvider>
    );

    expect(screen.getByTestId('device-alerts-list')).toBeInTheDocument();
    expect(screen.getByTestId('vitals-alerts-list')).toBeInTheDocument();
    expect(screen.getByText('100')).toHaveStyle({ color: '#FF4C42' });
  });

  it('highlights card if there is vitals alert', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <GraphCard
            bedData={{
              id: 'B-001',
              monitorId: 'PM-001',
              bedNo: 'Bed 1',
              patient: {
                patientId: 'P-001',
                patientPrimaryIdentifier: 'p-id-001',
                patientFirstName: 'John',
                patientLastName: 'Doe',
                patientGender: 'male',
                patientDob: '1990-01-01',
              },
            }}
            maxHeight='100px'
            elementId='E-001'
            metricName='ECG'
            showText={'bedInfo'}
            showAlerts={true}
            smallView={true}
            sendUpdateCallback={jest.fn()}
            alerts={[
              {
                type: ALERT_TYPES.VITALS,
                id: 'A-003',
                code: VITALS_ALERT_CODES.HR_LOW_VISUAL.code,
                deviceId: '40000',
                priority: 'HI',
                acknowledged: false,
                timestamp: '2023-07-20 09:26:48.035001',
              },
            ]}
            showSummary
            metrics={{
              hr: {
                value: 100,
                unit: '264864',
                timestamp: '2023-07-20T14:26:01.134',
              },
            }}
            hasActivePatientSession
          />
        </SessionContext>
      </QueryClientProvider>
    );

    expect(screen.getByTestId('graph-card-with-vitals-alert')).toBeInTheDocument();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.8.1.26
   */
  it('PM not available', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <GraphCard
            bedData={{
              id: 'B-001',
              monitorId: 'PM-001',
              bedNo: 'Bed 1',
              patient: {
                patientId: 'P-001',
                patientPrimaryIdentifier: 'p-id-001',
                patientFirstName: 'John',
                patientLastName: 'Doe',
                patientGender: 'male',
                patientDob: '1990-01-01',
              },
            }}
            elementId='E-001'
            metric={METRIC_INTERNAL_CODES.ECG}
            showText={'all'}
            showAlerts={false}
            smallView={false}
            sendUpdateCallback={jest.fn()}
            alertThresholds={MockAlertThresholds}
            metrics={{
              hr: {
                value: 100,
                unit: '264864',
                timestamp: '2023-07-20T14:26:01.134',
              },
            }}
            showSummary
            alerts={[
              {
                type: ALERT_TYPES.DEVICE,
                id: 'A-003',
                code: DEVICE_ALERT_CODES.MONITOR_NOT_AVAILABLE_ALERT.code,
                deviceId: 'DC-003',
                priority: 'LO',
                acknowledged: false,
                timestamp: '2023-07-20T10:26:01.134',
              },
            ]}
            hasActivePatientSession
          />
        </SessionContext>
      </QueryClientProvider>
    );

    expect(screen.getByText('PATIENT MONITOR IS NOT AVAILABLE')).toBeInTheDocument();
    expect(screen.getByTestId('alert-graph-card')).toHaveStyle({ backgroundColor: 'transparent' });
  });

  it('Technical alert high priority', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <GraphCard
            bedData={{
              id: 'B-001',
              monitorId: 'PM-001',
              bedNo: 'Bed 1',
              patient: {
                patientId: 'P-001',
                patientPrimaryIdentifier: 'p-id-001',
                patientFirstName: 'John',
                patientLastName: 'Doe',
                patientGender: 'male',
                patientDob: '1990-01-01',
              },
            }}
            elementId='E-001'
            metric={METRIC_INTERNAL_CODES.ECG}
            showText={'all'}
            showAlerts={true}
            smallView={false}
            sendUpdateCallback={jest.fn()}
            alertThresholds={MockAlertThresholds}
            metrics={{
              hr: {
                value: 100,
                unit: '264864',
                timestamp: '2023-07-20T14:26:01.134',
              },
            }}
            showSummary
            alerts={[
              {
                type: ALERT_TYPES.DEVICE,
                id: 'A-003',
                code: DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code,
                deviceCode: 'ANNE Chest',
                priority: 'HI',
                acknowledged: false,
                timestamp: '2023-07-20T10:26:01.134',
                waveformMessage: DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.waveformMessage,
              },
            ]}
            hasActivePatientSession
          />
        </SessionContext>
      </QueryClientProvider>
    );

    expect(
      screen.getByText(DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.waveformMessage)
    ).toBeInTheDocument();
    expect(screen.getByTestId('alert-graph-card')).toHaveStyle({
      backgroundColor: 'rgba(255, 76, 66, 0.25)',
    });
  });

  it('Technical alert medium priority', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <GraphCard
            bedData={{
              id: 'B-001',
              monitorId: 'PM-001',
              bedNo: 'Bed 1',
              patient: {
                patientId: 'P-001',
                patientPrimaryIdentifier: 'p-id-001',
                patientFirstName: 'John',
                patientLastName: 'Doe',
                patientGender: 'male',
                patientDob: '1990-01-01',
              },
            }}
            elementId='E-001'
            metric={METRIC_INTERNAL_CODES.ECG}
            showText={'all'}
            showAlerts={true}
            smallView={false}
            sendUpdateCallback={jest.fn()}
            alertThresholds={MockAlertThresholds}
            metrics={{
              hr: {
                value: 100,
                unit: '264864',
                timestamp: '2023-07-20T14:26:01.134',
              },
            }}
            showSummary
            alerts={[
              {
                type: ALERT_TYPES.DEVICE,
                id: 'A-003',
                code: DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code,
                deviceCode: 'ANNE Chest',
                priority: 'ME',
                acknowledged: false,
                timestamp: '2023-07-20T10:26:01.134',
                waveformMessage: DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.waveformMessage,
              },
            ]}
            hasActivePatientSession
          />
        </SessionContext>
      </QueryClientProvider>
    );

    expect(
      screen.getByText(DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.waveformMessage)
    ).toBeInTheDocument();
    expect(screen.getByTestId('alert-graph-card')).toHaveStyle({
      backgroundColor: 'rgba(246, 201, 5, 0.25)',
    });
  });

  it('Technical alert low priority', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <GraphCard
            bedData={{
              id: 'B-001',
              monitorId: 'PM-001',
              bedNo: 'Bed 1',
              patient: {
                patientId: 'P-001',
                patientPrimaryIdentifier: 'p-id-001',
                patientFirstName: 'John',
                patientLastName: 'Doe',
                patientGender: 'male',
                patientDob: '1990-01-01',
              },
            }}
            elementId='E-001'
            metric={METRIC_INTERNAL_CODES.ECG}
            showText={'all'}
            showAlerts={true}
            smallView={false}
            sendUpdateCallback={jest.fn()}
            alertThresholds={MockAlertThresholds}
            metrics={{
              hr: {
                value: 100,
                unit: '264864',
                timestamp: '2023-07-20T14:26:01.134',
              },
            }}
            showSummary
            alerts={[
              {
                type: ALERT_TYPES.DEVICE,
                id: 'A-003',
                code: DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code,
                deviceCode: 'ANNE Chest',
                priority: 'LO',
                acknowledged: false,
                timestamp: '2023-07-20T10:26:01.134',
                waveformMessage: DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.waveformMessage,
              },
            ]}
            hasActivePatientSession
          />
        </SessionContext>
      </QueryClientProvider>
    );

    expect(
      screen.getByText(DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.waveformMessage)
    ).toBeInTheDocument();
    expect(screen.getByTestId('alert-graph-card')).toHaveStyle({
      backgroundColor: 'rgba(117, 248, 252, 0.25)',
    });
  });
});
