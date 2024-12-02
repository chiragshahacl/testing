import { render, screen } from '@testing-library/react';

import VitalsTab from '@/app/(authenticated)/home/details/Tabs/VitalsTab';
import { ERROR_VALUE } from '@/constants';
import { SENSOR_TYPES } from '@/types/sensor';
import {
  ALERT_PRIORITY,
  DEVICE_ALERT_CODES,
  DEVICE_CODES,
  POSITION_TYPES,
  VITALS_ALERT_CODES,
} from '@/utils/metricCodes';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { alertThresholdsMock, metricsMock } from '../__mocks__/VitalsTabMocks';

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

describe('VitalsTab', () => {
  /*
   * Requirement IDs: RQ-00022-B: SR-1.3.2.1, SR-1.3.1.2, SR-1.5.2.1, SR-1.5.2.4, SR-1.5.2.5, SR-1.5.2.6, SR-1.5.2.7, SR-1.5.3.1, SR-1.5.3.5
   */
  it('renders all vitals cards', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <VitalsTab
          selectedBed={{
            bedNo: 'Bed 1',
            patient: {
              patientFirstName: 'John',
              patientLastName: 'Doe',
            },
          }}
          metrics={metricsMock}
          alertThresholds={alertThresholdsMock}
          sendNewDataSeries={jest.fn()}
          sendUpdateCallback={jest.fn()}
          vitalsAlerts={[]}
          deviceAlerts={[]}
          activeSensors={[]}
          isLoading={false}
        />
      </QueryClientProvider>
    );

    expect(screen.getByText('ECG')).toBeInTheDocument();
    expect(screen.getByText('HR (bpm)')).toBeInTheDocument();
    expect(screen.getByText('PLETH')).toBeInTheDocument();
    expect(screen.getByText('SPO2 (%)')).toBeInTheDocument();
    expect(screen.getByText('PR (bpm)')).toBeInTheDocument();
    expect(screen.getByText('PI (%)')).toBeInTheDocument();
    expect(screen.getByText('RR')).toBeInTheDocument();
    expect(screen.getByText('RR (brpm)')).toBeInTheDocument();
  });

  describe('shows empty value when sensors are not connected > ', () => {
    test.each([
      {
        id: '1',
        type: SENSOR_TYPES.CHEST,
      },
      {
        id: '2',
        type: SENSOR_TYPES.ADAM,
      },
    ])('one of HR and RR metric sensors are disconnected', async (sensors) => {
      render(
        <QueryClientProvider client={queryClient}>
          <VitalsTab
            selectedBed={{
              bedNo: 'Bed 1',
              patient: {
                patientFirstName: 'John',
                patientLastName: 'Doe',
              },
            }}
            hasActivePatientSession
            metrics={metricsMock}
            alertThresholds={alertThresholdsMock}
            sendNewDataSeries={jest.fn()}
            sendUpdateCallback={jest.fn()}
            vitalsAlerts={[]}
            deviceAlerts={[]}
            activeSensors={[sensors]}
            isLoading={false}
          />
        </QueryClientProvider>
      );

      expect(screen.getByTestId('hr-value-60')).toBeInTheDocument();
      expect(screen.getByTestId('rr-value-13')).toBeInTheDocument();
    });

    test.each([
      {
        id: '1',
        type: SENSOR_TYPES.LIMB,
      },
      {
        id: '2',
        type: SENSOR_TYPES.NONIN,
      },
    ])('one of SPO, PI, and PR sensors are disconnected', async (sensors) => {
      render(
        <QueryClientProvider client={queryClient}>
          <VitalsTab
            selectedBed={{
              bedNo: 'Bed 1',
              patient: {
                patientFirstName: 'John',
                patientLastName: 'Doe',
              },
            }}
            metrics={metricsMock}
            alertThresholds={alertThresholdsMock}
            sendNewDataSeries={jest.fn()}
            sendUpdateCallback={jest.fn()}
            vitalsAlerts={[]}
            deviceAlerts={[]}
            activeSensors={[sensors]}
            isLoading={false}
            hasActivePatientSession
          />
        </QueryClientProvider>
      );

      expect(screen.getByTestId('spo-value-98')).toBeInTheDocument();
      expect(screen.getByTestId('pr-value-64')).toBeInTheDocument();
      expect(screen.getByTestId('pi-value-15.0')).toBeInTheDocument();
    });
  });

  test.each([
    {
      id: 'A-001',
      type: DEVICE_CODES.ANNE_CHEST.type,
      code: DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code,
      deviceCode: 'ANNE Chest',
    },
    {
      id: 'A-002',
      type: DEVICE_CODES.ANNE_CHEST.type,
      code: DEVICE_ALERT_CODES.SENSOR_FAILURE_ALERT.code,
      deviceCode: 'ANNE Chest',
    },
    {
      id: 'A-003',
      type: DEVICE_CODES.ANNE_CHEST.type,
      code: DEVICE_ALERT_CODES.LEAD_OFF_ALERT.code,
      deviceCode: 'ANNE Chest',
    },
    {
      id: 'A-004',
      type: DEVICE_CODES.NONIN_3150.type,
      code: DEVICE_ALERT_CODES.POOR_SKIN_CONTACT_ALERT.code,
      deviceCode: 'Nonin 3150',
    },
    {
      id: 'A-005',
      type: DEVICE_CODES.NONIN_3150.type,
      code: DEVICE_ALERT_CODES.SENSOR_ERROR_ALERT.code,
      deviceCode: 'Nonin 3150',
    },
    {
      id: 'A-006',
      type: DEVICE_CODES.NONIN_3150.type,
      code: DEVICE_ALERT_CODES.SYSTEM_ERROR_ALERT.code,
      deviceCode: 'Nonin 3150',
    },
    {
      id: 'A-007',
      type: DEVICE_CODES.NONIN_3150.type,
      code: DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code,
      deviceCode: 'Nonin 3150',
    },
    {
      id: 'A-008',
      type: DEVICE_CODES.ANNE_LIMB.type,
      code: DEVICE_ALERT_CODES.POOR_SKIN_CONTACT_ALERT.code,
      deviceCode: 'ANNE Limb',
    },
    {
      id: 'A-009',
      type: DEVICE_CODES.ANNE_LIMB.type,
      code: DEVICE_ALERT_CODES.SENSOR_FAILURE_ALERT.code,
      deviceCode: 'ANNE Limb',
    },
    {
      id: 'A-010',
      type: DEVICE_CODES.ANNE_LIMB.type,
      code: DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code,
      deviceCode: 'ANNE Limb',
    },
    {
      id: 'A-011',
      type: DEVICE_CODES.ADAM.type,
      code: DEVICE_ALERT_CODES.POOR_SKIN_CONTACT_ALERT.code,
      deviceCode: 'ADAM',
    },
    {
      id: 'A-012',
      type: DEVICE_CODES.ADAM.type,
      code: DEVICE_ALERT_CODES.SENSOR_FAILURE_ALERT.code,
      deviceCode: 'ADAM',
    },
    {
      id: 'A-013',
      type: DEVICE_CODES.ADAM.type,
      code: DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code,
      deviceCode: 'ADAM',
    },
    {
      id: 'A-014',
      type: DEVICE_CODES.VIATOM_BP.type,
      code: DEVICE_ALERT_CODES.LOOSE_SLEEVE_ALERT.code,
      deviceCode: 'Viatom BP monitor',
    },
    {
      id: 'A-015',
      type: DEVICE_CODES.VIATOM_BP.type,
      code: DEVICE_ALERT_CODES.MOVEMENT_DETECTED_ALERT.code,
      deviceCode: 'Viatom BP monitor',
    },
    {
      id: 'A-016',
      type: DEVICE_CODES.VIATOM_BP.type,
      code: DEVICE_ALERT_CODES.WEAK_PULSE_ALERT.code,
      deviceCode: 'Viatom BP monitor',
    },
    {
      id: 'A-016',
      type: DEVICE_CODES.VIATOM_BP.type,
      code: DEVICE_ALERT_CODES.SENSOR_FAILURE_ALERT.code,
      deviceCode: 'Viatom BP monitor',
    },
  ])('renders error value based on technical alert', async (alert) => {
    render(
      <QueryClientProvider client={queryClient}>
        <VitalsTab
          selectedBed={{
            bedNo: 'Bed 1',
            patient: {
              patientFirstName: 'John',
              patientLastName: 'Doe',
            },
          }}
          hasActivePatientSession
          metrics={metricsMock}
          alertThresholds={alertThresholdsMock}
          sendNewDataSeries={jest.fn()}
          sendUpdateCallback={(_, metricsSetter) => {
            metricsSetter({
              position: [POSITION_TYPES.SUPINE],
              timestamp: new Date().toISOString(),
            });
          }}
          vitalsAlerts={[]}
          deviceAlerts={[alert]}
          activeSensors={[
            {
              id: '1',
              type: SENSOR_TYPES.CHEST,
            },
            {
              id: '2',
              type: SENSOR_TYPES.ADAM,
            },
            {
              id: '3',
              type: SENSOR_TYPES.LIMB,
            },
            {
              id: '4',
              type: SENSOR_TYPES.NONIN,
            },
            {
              id: '5',
              type: SENSOR_TYPES.BP,
            },
            {
              id: '6',
              type: SENSOR_TYPES.THERMOMETER,
            },
          ]}
          isLoading={false}
        />
      </QueryClientProvider>
    );

    if (
      alert.type === DEVICE_CODES.VIATOM_BP.type &&
      (alert.code === DEVICE_ALERT_CODES.LOOSE_SLEEVE_ALERT.code ||
        alert.code === DEVICE_ALERT_CODES.MOVEMENT_DETECTED_ALERT.code ||
        alert.code === DEVICE_ALERT_CODES.WEAK_PULSE_ALERT.code ||
        alert.code === DEVICE_ALERT_CODES.SENSOR_FAILURE_ALERT.code)
    ) {
      expect(screen.getByTestId(/pulse-metric-card/)).toHaveTextContent(ERROR_VALUE);
      expect(screen.getByTestId(/bp-metric-card/)).toHaveTextContent(ERROR_VALUE);
    } else if (
      alert.type === DEVICE_CODES.ADAM.type &&
      (alert.code === DEVICE_ALERT_CODES.POOR_SKIN_CONTACT_ALERT.code ||
        alert.code === DEVICE_ALERT_CODES.MODULE_FAILURE_ALERT.code ||
        alert.code === DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code)
    ) {
      expect(screen.getByTestId('hr-value--?-')).toHaveTextContent(ERROR_VALUE);
      expect(screen.getByTestId('rr-value--?-')).toHaveTextContent(ERROR_VALUE);
      expect(screen.getByTestId(/chest-temp-metric-card/)).toHaveTextContent(ERROR_VALUE);
      expect(screen.getByTestId(/fall-metric-card/)).toHaveTextContent(ERROR_VALUE);
      expect(screen.getByTestId(/position-metric-card/)).toHaveTextContent(ERROR_VALUE);
    } else if (
      alert.type === DEVICE_CODES.ANNE_LIMB.type &&
      (alert.code === DEVICE_ALERT_CODES.POOR_SKIN_CONTACT_ALERT.code ||
        alert.code === DEVICE_ALERT_CODES.MODULE_FAILURE_ALERT.code ||
        alert.code === DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code)
    ) {
      expect(screen.getByTestId('spo-value--?-')).toHaveTextContent(ERROR_VALUE);
      expect(screen.getByTestId('pi-value--?-')).toHaveTextContent(ERROR_VALUE);
      expect(screen.getByTestId('pr-value--?-')).toHaveTextContent(ERROR_VALUE);
      expect(screen.getByTestId(/limb-temp-metric-card/)).toHaveTextContent(ERROR_VALUE);
    } else if (
      alert.type === DEVICE_CODES.NONIN_3150.type &&
      (alert.code === DEVICE_ALERT_CODES.FINGER_NOT_DETECTED_ALERT.code ||
        alert.code === DEVICE_ALERT_CODES.SENSOR_ERROR_ALERT.code ||
        alert.code === DEVICE_ALERT_CODES.SYSTEM_ERROR_ALERT.code ||
        alert.code === DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code)
    ) {
      expect(screen.getByTestId('spo-value--?-')).toHaveTextContent(ERROR_VALUE);
      expect(screen.getByTestId('pi-value--?-')).toHaveTextContent(ERROR_VALUE);
      expect(screen.getByTestId('pr-value--?-')).toHaveTextContent(ERROR_VALUE);
    } else if (
      alert.type === DEVICE_CODES.ANNE_CHEST.type &&
      (alert.code === DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code ||
        alert.code === DEVICE_ALERT_CODES.MODULE_FAILURE_ALERT.code ||
        alert.code === DEVICE_ALERT_CODES.LEAD_OFF_ALERT.code)
    ) {
      expect(screen.getByTestId('hr-value--?-')).toHaveTextContent(ERROR_VALUE);
      expect(screen.getByTestId('rr-value--?-')).toHaveTextContent(ERROR_VALUE);
      expect(screen.getByTestId(/chest-temp-metric-card/)).toHaveTextContent(ERROR_VALUE);
      expect(screen.getByTestId(/fall-metric-card/)).toHaveTextContent(ERROR_VALUE);
      expect(screen.getByTestId(/position-metric-card/)).toHaveTextContent(ERROR_VALUE);
    }
  });

  test.each([
    {
      id: 'A-001',
      code: VITALS_ALERT_CODES.HR_HIGH_VISUAL.code,
      priority: ALERT_PRIORITY.HIGH,
      timestamp: '2023-07-20T09:26:01.134',
    },
    {
      id: 'A-002',
      code: VITALS_ALERT_CODES.RR_LOW_VISUAL.code,
      priority: ALERT_PRIORITY.MEDIUM,
      timestamp: '2023-07-20T10:26:01.134',
    },
    {
      id: 'A-003',
      code: VITALS_ALERT_CODES.SPO2_LOW_VISUAL.code,
      priority: ALERT_PRIORITY.LOW,
      timestamp: '2023-07-20T11:26:01.134',
    },
    {
      id: 'A-004',
      code: VITALS_ALERT_CODES.SYS_LOW_VISUAL.code,
      priority: ALERT_PRIORITY.MEDIUM,
      timestamp: '2023-07-20T12:26:01.134',
    },
    {
      id: 'A-005',
      code: VITALS_ALERT_CODES.BODY_TEMP_LOW_VISUAL.code,
      priority: ALERT_PRIORITY.MEDIUM,
      timestamp: '2023-07-20T13:26:01.134',
    },
    {
      id: 'A-006',
      code: VITALS_ALERT_CODES.CHEST_TEMP_LOW_VISUAL.code,
      priority: ALERT_PRIORITY.MEDIUM,
      deviceCode: SENSOR_TYPES.ADAM,
      timestamp: '2023-07-20T14:26:01.134',
    },
    {
      id: 'A-007',
      code: VITALS_ALERT_CODES.LIMB_TEMP_LOW_VISUAL.code,
      priority: ALERT_PRIORITY.MEDIUM,
      deviceCode: SENSOR_TYPES.LIMB,
      timestamp: '2023-07-20T14:26:01.134',
    },
    {
      id: 'A-008',
      code: VITALS_ALERT_CODES.FALL_VISUAL.code,
      priority: ALERT_PRIORITY.MEDIUM,
      timestamp: '2023-07-20T15:26:01.134',
    },
    {
      id: 'A-009',
      code: VITALS_ALERT_CODES.POSITION_VISUAL.code,
      priority: ALERT_PRIORITY.LOW,
      timestamp: '2023-07-20T16:26:01.134',
    },
  ])('highlights metric card based on alert severity', async (alert) => {
    render(
      <QueryClientProvider client={queryClient}>
        <VitalsTab
          selectedBed={{
            bedNo: 'Bed 1',
            patient: {
              patientFirstName: 'John',
              patientLastName: 'Doe',
            },
          }}
          metrics={metricsMock}
          hasActivePatientSession
          alertThresholds={alertThresholdsMock}
          sendNewDataSeries={jest.fn()}
          sendUpdateCallback={(_, metricsSetter) => {
            metricsSetter({
              position: [POSITION_TYPES.SUPINE],
              timestamp: new Date().toISOString(),
            });
          }}
          vitalsAlerts={[alert]}
          deviceAlerts={[]}
          activeSensors={[
            {
              id: '1',
              type: SENSOR_TYPES.CHEST,
            },
            {
              id: '2',
              type: SENSOR_TYPES.ADAM,
            },
            {
              id: '3',
              type: SENSOR_TYPES.LIMB,
            },
            {
              id: '4',
              type: SENSOR_TYPES.NONIN,
            },
            {
              id: '5',
              type: SENSOR_TYPES.BP,
            },
            {
              id: '6',
              type: SENSOR_TYPES.THERMOMETER,
            },
          ]}
          isLoading={false}
        />
      </QueryClientProvider>
    );

    if (alert.id === 'A-001') {
      expect(screen.getByTestId('hr-metric-card')).toHaveClass('metricCardWithHighAlert');
    } else if (alert.id === 'A-002') {
      expect(screen.getByTestId('rr-metric-card')).toHaveClass('metricCardWithMedAlert');
    } else if (alert.id === 'A-003') {
      expect(screen.getByTestId('spo-metric-field')).toHaveClass('metricCardWithLowAlert');
    } else if (alert.id === 'A-004') {
      expect(screen.getByTestId(/bp-metric-card/)).toHaveClass('metricCardWithMedAlert');
    } else if (alert.id === 'A-005') {
      expect(screen.getByTestId(/body-temp-metric-card/)).toHaveClass('metricCardWithMedAlert');
    } else if (alert.id === 'A-006') {
      expect(screen.getByTestId(/chest-temp-metric-card/)).toHaveClass('metricCardWithMedAlert');
    } else if (alert.id === 'A-007') {
      expect(screen.getByTestId(/limb-temp-metric-card/)).toHaveClass('metricCardWithMedAlert');
    } else if (alert.id === 'A-008') {
      expect(screen.getByTestId(/fall-metric-card/)).toHaveClass('metricCardWithMedAlert');
    } else if (alert.id === 'A-009') {
      expect(screen.getByTestId(/position-metric-card/)).toHaveClass('metricCardWithLowAlert');
    }
  });
});
