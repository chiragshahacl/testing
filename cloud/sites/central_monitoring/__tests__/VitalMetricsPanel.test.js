import { render, screen } from '@testing-library/react';

import VitalMetricsPanel from '@/app/(authenticated)/home/details/VitalMetricsPanel';
import { SENSOR_TYPES } from '@/types/sensor';
import { ERROR_VALUE } from '@/constants';
import { ALERT_PRIORITY, METRIC_INTERNAL_CODES, POSITION_TYPES } from '@/utils/metricCodes';
import { alertThresholdsMock, metricsMock } from '../__mocks__/VitalMetricsPanelMocks';
import moment from 'moment';
import { timeFromNow } from '@/utils/moment';

describe('VitalMetricsPanel', () => {
  it('renders initial state', async () => {
    render(
      <VitalMetricsPanel
        metrics={metricsMock}
        alertThresholds={alertThresholdsMock}
        vitalsAlertSeverities={{
          [METRIC_INTERNAL_CODES.NIBP]: null,
          [METRIC_INTERNAL_CODES.BODY_TEMP]: null,
          [METRIC_INTERNAL_CODES.CHEST_TEMP]: null,
          [METRIC_INTERNAL_CODES.LIMB_TEMP]: null,
          [METRIC_INTERNAL_CODES.FALLS]: null,
          [METRIC_INTERNAL_CODES.POSITION]: null,
        }}
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
        technicalAlerts={{
          HR: false,
          SPO: false,
          PI: false,
          PR: false,
          RR: false,
          FALLS: false,
          BODY_POSITION: false,
          PULSE: false,
          NIBP: false,
          CHEST_TEMP: false,
        }}
      />
    );

    expect(screen.getByText('PULSE (bpm)')).toBeInTheDocument();
    expect(screen.getByText('160')).toBeInTheDocument();
    expect(screen.getByText('90')).toBeInTheDocument();
    expect(screen.getByText('110')).toBeInTheDocument();
    expect(screen.getByText('50')).toBeInTheDocument();
    expect(screen.getByText('NIBP (mmHg)')).toBeInTheDocument();
    expect(screen.getAllByText('102.2')).toHaveLength(3);
    expect(screen.getAllByText('93.2')).toHaveLength(3);
    expect(screen.getByText('40°')).toBeInTheDocument();
    expect(screen.getByTestId('metric-value-nibp-map-130')).toBeInTheDocument();
    expect(screen.getByText('BODY TEMP (°F)')).toBeInTheDocument();
    expect(screen.getByText('SKIN TEMP (°F)')).toBeInTheDocument();
    expect(screen.getByText('CHEST TEMP')).toBeInTheDocument();
    expect(screen.getByText('LIMB TEMP')).toBeInTheDocument();
    expect(screen.getByText('FALL')).toBeInTheDocument();
    expect(screen.getByText('Supine')).toBeInTheDocument();
  });

  it('shows loading when checking for sensor connection', async () => {
    render(
      <VitalMetricsPanel
        metrics={{}}
        alertThresholds={alertThresholdsMock}
        vitalsAlertSeverities={{
          [METRIC_INTERNAL_CODES.NIBP]: null,
          [METRIC_INTERNAL_CODES.BODY_TEMP]: null,
          [METRIC_INTERNAL_CODES.CHEST_TEMP]: null,
          [METRIC_INTERNAL_CODES.LIMB_TEMP]: null,
          [METRIC_INTERNAL_CODES.FALLS]: null,
          [METRIC_INTERNAL_CODES.POSITION]: null,
        }}
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
        isLoading
        technicalAlerts={{
          HR: false,
          SPO: false,
          PI: false,
          PR: false,
          RR: false,
          FALLS: false,
          BODY_POSITION: false,
          PULSE: false,
          NIBP: false,
          CHEST_TEMP: false,
        }}
      />
    );

    expect(screen.getAllByRole('progressbar')).toHaveLength(5);
    expect(screen.getByText('PULSE (bpm)')).toBeInTheDocument();
    expect(screen.getByText('160')).toBeInTheDocument();
    expect(screen.getByText('90')).toBeInTheDocument();
    expect(screen.getByText('110')).toBeInTheDocument();
    expect(screen.getByText('50')).toBeInTheDocument();
    expect(screen.getByText('NIBP (mmHg)')).toBeInTheDocument();
    expect(screen.getAllByText('102.2')).toHaveLength(3);
    expect(screen.getAllByText('93.2')).toHaveLength(3);
    expect(screen.getByText('BODY TEMP (°F)')).toBeInTheDocument();
    expect(screen.getByText('SKIN TEMP (°F)')).toBeInTheDocument();
    expect(screen.getByText('CHEST TEMP')).toBeInTheDocument();
    expect(screen.getByText('LIMB TEMP')).toBeInTheDocument();
    expect(screen.getByText('FALL')).toBeInTheDocument();
    expect(screen.getByText('Body Position')).toBeInTheDocument();
  });

  it('shows loading non-continuous vitals even when sensor is disconnected', async () => {
    render(
      <VitalMetricsPanel
        metrics={{
          dia: { value: 30, unit: 'mmHg' },
          sys: { value: 35, unit: 'mmHg' },
          pulse: { value: 25, unit: 'bpm' },
          bodyTemp: { value: 20.0, unit: '°F' },
        }}
        alertThresholds={alertThresholdsMock}
        vitalsAlertSeverities={{
          [METRIC_INTERNAL_CODES.NIBP]: null,
          [METRIC_INTERNAL_CODES.BODY_TEMP]: null,
          [METRIC_INTERNAL_CODES.CHEST_TEMP]: null,
          [METRIC_INTERNAL_CODES.LIMB_TEMP]: null,
          [METRIC_INTERNAL_CODES.FALLS]: null,
          [METRIC_INTERNAL_CODES.POSITION]: null,
        }}
        activeSensors={[]}
        isLoading
        technicalAlerts={{
          HR: false,
          SPO: false,
          PI: false,
          PR: false,
          RR: false,
          FALLS: false,
          BODY_POSITION: false,
          PULSE: false,
          NIBP: false,
          CHEST_TEMP: false,
        }}
      />
    );

    expect(screen.getByText('20.0')).toBeInTheDocument();
    expect(screen.getByText('25')).toBeInTheDocument();
    expect(screen.getByText('30')).toBeInTheDocument();
    expect(screen.getByText('35')).toBeInTheDocument();
  });

  describe('disables metric and shows empty data when sensor is not connected', () => {
    it('all LIMB_TEMP sensors are disconnected', async () => {
      render(
        <VitalMetricsPanel
          metrics={metricsMock}
          alertThresholds={alertThresholdsMock}
          vitalsAlertSeverities={{
            [METRIC_INTERNAL_CODES.NIBP]: null,
            [METRIC_INTERNAL_CODES.BODY_TEMP]: null,
            [METRIC_INTERNAL_CODES.CHEST_TEMP]: null,
            [METRIC_INTERNAL_CODES.LIMB_TEMP]: null,
            [METRIC_INTERNAL_CODES.FALLS]: null,
            [METRIC_INTERNAL_CODES.POSITION]: null,
          }}
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
          technicalAlerts={{
            HR: false,
            SPO: false,
            PI: false,
            PR: false,
            RR: false,
            FALLS: false,
            BODY_POSITION: false,
            PULSE: false,
            NIBP: false,
            CHEST_TEMP: false,
          }}
        />
      );

      expect(screen.getByTestId(/limb-temp-sensors-not-connected/)).toBeInTheDocument();

      expect(screen.getByTestId(/metric-value-pulse-100/)).toBeInTheDocument();
      expect(screen.getByTestId('metric-value-nibp-sys-120')).toBeInTheDocument();
      expect(screen.getByTestId('metric-value-nibp-dia-80')).toBeInTheDocument();
      expect(screen.getByTestId(/metric-value-body-temp-99/)).toBeInTheDocument();
      expect(screen.getByTestId(/metric-value-chest-temp-99.8/)).toBeInTheDocument();

      expect(screen.getByText('160')).toBeInTheDocument();
      expect(screen.getByText('90')).toBeInTheDocument();
      expect(screen.getByText('110')).toBeInTheDocument();
      expect(screen.getByText('50')).toBeInTheDocument();
      expect(screen.getAllByText('102.2')).toHaveLength(3);
      expect(screen.getAllByText('93.2')).toHaveLength(3);
    });

    test.each([
      {
        id: '1',
        type: SENSOR_TYPES.CHEST,
      },
      {
        id: '1',
        type: SENSOR_TYPES.ADAM,
      },
    ])('some BODY_POSITION sensors are disconnected', async (sensors) => {
      render(
        <VitalMetricsPanel
          metrics={metricsMock}
          alertThresholds={alertThresholdsMock}
          vitalsAlertSeverities={{
            [METRIC_INTERNAL_CODES.NIBP]: null,
            [METRIC_INTERNAL_CODES.BODY_TEMP]: null,
            [METRIC_INTERNAL_CODES.CHEST_TEMP]: null,
            [METRIC_INTERNAL_CODES.LIMB_TEMP]: null,
            [METRIC_INTERNAL_CODES.FALLS]: null,
            [METRIC_INTERNAL_CODES.POSITION]: null,
          }}
          activeSensors={[sensors]}
          isLoading={false}
          technicalAlerts={{
            HR: false,
            SPO: false,
            PI: false,
            PR: false,
            RR: false,
            FALLS: false,
            BODY_POSITION: false,
            PULSE: false,
            NIBP: false,
            CHEST_TEMP: false,
          }}
        />
      );

      expect(screen.getByTestId(/position-sensors-connected/)).toBeInTheDocument();
    });

    it('all BODY_POSITION sensors are disconnected', async () => {
      render(
        <VitalMetricsPanel
          metrics={metricsMock}
          alertThresholds={alertThresholdsMock}
          vitalsAlertSeverities={{
            [METRIC_INTERNAL_CODES.NIBP]: null,
            [METRIC_INTERNAL_CODES.BODY_TEMP]: null,
            [METRIC_INTERNAL_CODES.CHEST_TEMP]: null,
            [METRIC_INTERNAL_CODES.LIMB_TEMP]: null,
            [METRIC_INTERNAL_CODES.FALLS]: null,
            [METRIC_INTERNAL_CODES.POSITION]: null,
          }}
          activeSensors={[
            {
              id: '2',
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
          technicalAlerts={{
            HR: false,
            SPO: false,
            PI: false,
            PR: false,
            RR: false,
            FALLS: false,
            BODY_POSITION: false,
            PULSE: false,
            NIBP: false,
            CHEST_TEMP: false,
          }}
        />
      );

      expect(screen.getByTestId(/position-sensors-not-connected/)).toBeInTheDocument();

      expect(screen.getByTestId(/limb-temp-sensors-connected/)).toBeInTheDocument();
      expect(screen.getByTestId(/metric-value-limb-temp-99.9/)).toBeInTheDocument();
      expect(screen.getByTestId(/metric-value-pulse-100/)).toBeInTheDocument();
      expect(screen.getByTestId('metric-value-nibp-sys-120')).toBeInTheDocument();
      expect(screen.getByTestId('metric-value-nibp-dia-80')).toBeInTheDocument();
      expect(screen.getByTestId(/metric-value-body-temp-99/)).toBeInTheDocument();

      expect(screen.getByText('160')).toBeInTheDocument();
      expect(screen.getByText('90')).toBeInTheDocument();
      expect(screen.getByText('110')).toBeInTheDocument();
      expect(screen.getByText('50')).toBeInTheDocument();
      expect(screen.getAllByText('102.2')).toHaveLength(3);
      expect(screen.getAllByText('93.2')).toHaveLength(3);
    });
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.3.3.21, SR-1.3.3.23
   */
  it('renders vitals value when sensors are connected and does not have technical alerts', async () => {
    render(
      <VitalMetricsPanel
        metrics={metricsMock}
        alertThresholds={alertThresholdsMock}
        vitalsAlertSeverities={{
          [METRIC_INTERNAL_CODES.NIBP]: null,
          [METRIC_INTERNAL_CODES.BODY_TEMP]: null,
          [METRIC_INTERNAL_CODES.CHEST_TEMP]: null,
          [METRIC_INTERNAL_CODES.LIMB_TEMP]: null,
          [METRIC_INTERNAL_CODES.FALLS]: null,
          [METRIC_INTERNAL_CODES.POSITION]: null,
        }}
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
        technicalAlerts={{
          HR: false,
          SPO: false,
          PI: false,
          PR: false,
          RR: false,
          FALLS: false,
          BODY_POSITION: false,
          PULSE: false,
          NIBP: false,
          CHEST_TEMP: false,
        }}
      />
    );

    expect(screen.getByText('160')).toBeInTheDocument();
    expect(screen.getByText('90')).toBeInTheDocument();
    expect(screen.getByText('120')).toBeInTheDocument();
    expect(screen.getByText('110')).toBeInTheDocument();
    expect(screen.getByText('50')).toBeInTheDocument();
    expect(screen.getByText('80')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument();
    expect(screen.getByText('99.0')).toBeInTheDocument();
    expect(screen.getByText('99.9')).toBeInTheDocument();
    expect(screen.getByText('99.8')).toBeInTheDocument();
    expect(screen.getByText('40°')).toBeInTheDocument();
    expect(screen.getByTestId('metric-value-nibp-map-130')).toBeInTheDocument();
    expect(screen.getByText('NOT DETECTED')).toBeInTheDocument();
    expect(screen.getByText('Supine')).toBeInTheDocument();
    expect(screen.getByText('Lasted')).toBeInTheDocument();
    expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.4.1.7, SR-1.4.2.7 RQ-00022-B: SR-1.3.15.48
   */
  test.each(['FALLS', 'BODY_POSITION', 'PULSE', 'NIBP', 'BODY_TEMP', 'CHEST_TEMP', 'LIMB_TEMP'])(
    'renders error value when sensors are connected and have technical alerts',
    async (vitals) => {
      render(
        <VitalMetricsPanel
          metrics={metricsMock}
          alertThresholds={alertThresholdsMock}
          vitalsAlertSeverities={{
            [METRIC_INTERNAL_CODES.NIBP]: null,
            [METRIC_INTERNAL_CODES.BODY_TEMP]: null,
            [METRIC_INTERNAL_CODES.CHEST_TEMP]: null,
            [METRIC_INTERNAL_CODES.LIMB_TEMP]: null,
            [METRIC_INTERNAL_CODES.FALLS]: null,
            [METRIC_INTERNAL_CODES.POSITION]: null,
          }}
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
          technicalAlerts={{
            HR: false,
            SPO: false,
            PI: false,
            PR: false,
            RR: false,
            FALLS: vitals === 'FALLS',
            BODY_POSITION: vitals === 'BODY_POSITION',
            PULSE: vitals === 'PULSE',
            NIBP: vitals === 'NIBP',
            CHEST_TEMP: vitals === 'CHEST_TEMP',
            BODY_TEMP: vitals === 'BODY_TEMP',
            LIMB_TEMP: vitals === 'LIMB_TEMP',
          }}
        />
      );

      let elem;
      switch (vitals) {
        case 'PULSE':
          elem = screen.getByTestId(/pulse-metric-card/);
          break;
        case 'FALLS':
          elem = screen.getByTestId(/fall-metric-card/);
          break;
        case 'BODY_POSITION':
          elem = screen.getByTestId(/position-metric-card/);
          break;
        case 'NIBP':
          elem = screen.getByTestId(/bp-metric-card/);
          break;
        case 'CHEST_TEMP':
          elem = screen.getByTestId(/chest-temp-metric-card/);
          break;
        case 'LIMB_TEMP':
          elem = screen.getByTestId(/limb-temp-metric-card/);
          break;
        case 'BODY_TEMP':
          elem = screen.getByTestId(/body-temp-metric-card/);
          break;
        default:
          elem = null;
      }
      expect(elem).toHaveTextContent(ERROR_VALUE);
    }
  );

  /*
   * Requirement IDs: RQ-00022-B: SR-1.3.5.30, SR-1.3.5.27
   */
  it('renders alert ui', async () => {
    render(
      <VitalMetricsPanel
        metrics={{ ...metricsMock, falls: { value: 1, unit: '' } }}
        alertThresholds={alertThresholdsMock}
        vitalsAlertSeverities={{
          [METRIC_INTERNAL_CODES.NIBP]: ALERT_PRIORITY.MEDIUM,
          [METRIC_INTERNAL_CODES.BODY_TEMP]: ALERT_PRIORITY.MEDIUM,
          [METRIC_INTERNAL_CODES.CHEST_TEMP]: ALERT_PRIORITY.MEDIUM,
          [METRIC_INTERNAL_CODES.LIMB_TEMP]: ALERT_PRIORITY.MEDIUM,
          [METRIC_INTERNAL_CODES.FALLS]: ALERT_PRIORITY.MEDIUM,
          [METRIC_INTERNAL_CODES.POSITION]: ALERT_PRIORITY.LOW,
        }}
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
        technicalAlerts={{
          HR: false,
          SPO: false,
          PI: false,
          PR: false,
          RR: false,
          FALLS: false,
          BODY_POSITION: false,
          PULSE: false,
          NIBP: false,
          CHEST_TEMP: false,
        }}
      />
    );

    expect(screen.getByTestId(/bp-metric-card/)).toHaveClass('metricCardWithMedAlert');
    expect(screen.getByTestId(/body-temp-metric-card/)).toHaveClass('metricCardWithMedAlert');
    expect(screen.getByTestId(/chest-temp-metric-card/)).toHaveClass('metricCardWithMedAlert');
    expect(screen.getByTestId(/limb-temp-metric-card/)).toHaveClass('metricCardWithMedAlert');
    expect(screen.getByTestId(/fall-metric-card/)).toHaveClass('metricCardWithMedAlert');
    expect(screen.getByText('DETECTED')).toBeInTheDocument();
    expect(screen.getByTestId(/position-metric-card/)).toHaveClass('metricCardWithLowAlert');
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.3.3.21, SR-1.3.13.22 RQ-00022-B: SR-1.3.3.21, SR-1.3.13.22 RQ-00022-B: SR-1.3.3.21, SR-1.3.13.22 RQ-00022-B: SR-1.3.3.21, SR-1.3.13.22 RQ-00022-B: SR-1.3.3.21, SR-1.3.13.22
   */
  test.each([
    POSITION_TYPES.SUPINE,
    POSITION_TYPES.PRONE,
    POSITION_TYPES.UPRIGHT,
    POSITION_TYPES.RIGHTL,
    POSITION_TYPES.LEFTL,
  ])('renders proper body position icon', async (testPosition) => {
    render(
      <VitalMetricsPanel
        metrics={{ ...metricsMock, position: { value: testPosition, unit: '' } }}
        alertThresholds={alertThresholdsMock}
        vitalsAlertSeverities={{
          [METRIC_INTERNAL_CODES.NIBP]: null,
          [METRIC_INTERNAL_CODES.BODY_TEMP]: null,
          [METRIC_INTERNAL_CODES.CHEST_TEMP]: null,
          [METRIC_INTERNAL_CODES.LIMB_TEMP]: null,
          [METRIC_INTERNAL_CODES.FALLS]: null,
          [METRIC_INTERNAL_CODES.POSITION]: null,
        }}
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
        technicalAlerts={{
          HR: false,
          SPO: false,
          PI: false,
          PR: false,
          RR: false,
          FALLS: false,
          BODY_POSITION: false,
          PULSE: false,
          NIBP: false,
          CHEST_TEMP: false,
        }}
      />
    );

    expect(screen.getByTestId(`${testPosition.toLowerCase()}-position`)).toBeInTheDocument();
  });

  test.each([
    [0, 1],
    [0, 1],
  ])('shows correct timestamp for NIBP', async (sys_timestamp, dia_timestamp) => {
    const generateCurrentTimestamp = (ago = 0) => {
      const now = moment().subtract(ago, 'hours');
      const timestamp = now.format('YYYY-MM-DDTHH:mm:ss.SSS');
      const microseconds = now.format('SSSSSS').slice(3);
      return `${timestamp}${microseconds}Z`;
    };

    render(
      <VitalMetricsPanel
        metrics={{
          dia: { value: 80, unit: 'mmHg', timestamp: generateCurrentTimestamp(dia_timestamp) },
          sys: { value: 120, unit: 'mmHg', timestamp: generateCurrentTimestamp(sys_timestamp) },
          map: { value: 130, unit: '' },
          pulse: { value: 100, unit: 'bpm' },
          bodyTemp: { value: 99.0, unit: '°F' },
          limbTemp: { value: 99.9, unit: '°F' },
          chestTemp: { value: 99.8, unit: '°F' },
          falls: { value: 0, unit: '' },
          positionDuration: { value: 35, unit: '' },
          position: { value: POSITION_TYPES.SUPINE, unit: '' },
        }}
        alertThresholds={alertThresholdsMock}
        vitalsAlertSeverities={{
          [METRIC_INTERNAL_CODES.NIBP]: null,
          [METRIC_INTERNAL_CODES.BODY_TEMP]: null,
          [METRIC_INTERNAL_CODES.CHEST_TEMP]: null,
          [METRIC_INTERNAL_CODES.LIMB_TEMP]: null,
          [METRIC_INTERNAL_CODES.FALLS]: null,
          [METRIC_INTERNAL_CODES.POSITION]: null,
        }}
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
        technicalAlerts={{
          HR: false,
          SPO: false,
          PI: false,
          PR: false,
          RR: false,
          FALLS: false,
          BODY_POSITION: false,
          PULSE: false,
          NIBP: false,
          CHEST_TEMP: false,
        }}
      />
    );

    expect(screen.getByTestId('NIBP (mmHg)-subtitle')).toHaveTextContent(
      timeFromNow(generateCurrentTimestamp())
    );
  });
});
