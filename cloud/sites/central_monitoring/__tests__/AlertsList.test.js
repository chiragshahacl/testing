import AlertList from '@/components/lists/AlertList';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import { SENSOR_CODES, SENSOR_TYPES } from '@/types/sensor';
import {
  ALERT_PRIORITY,
  ALERT_TYPES,
  DEVICE_ALERT_CODES,
  VITALS_ALERT_CODES,
} from '@/utils/metricCodes';

describe('AlertList', () => {
  it('renders all components', async () => {
    render(<AlertList deviceAlerts={[]} vitalsAlerts={[]} />);

    expect(screen.queryByTestId('device-alerts-list')).not.toBeInTheDocument();
    expect(screen.queryByTestId('vitals-alerts-list')).not.toBeInTheDocument();
  });

  it('renders both alerts', async () => {
    render(
      <AlertList
        deviceAlerts={[
          {
            type: ALERT_TYPES.DEVICE,
            id: 'A-001',
            code: 'C-001',
            deviceId: 'DC-001',
            priority: ALERT_PRIORITY.LOW,
            acknowledged: false,
          },
        ]}
        vitalsAlerts={[
          {
            type: ALERT_TYPES.VITALS,
            id: 'A-001',
            code: '30013',
            deviceId: '40000',
            priority: ALERT_PRIORITY.LOW,
            acknowledged: false,
          },
        ]}
      />
    );

    expect(screen.getByTestId('device-alerts-list')).toBeInTheDocument();
    expect(screen.getByTestId('vitals-alerts-list')).toBeInTheDocument();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.5.2.5, SR-1.4.1.1, SR-1.4.1.2, SR-1.4.1.4 RQ-00022-B: SR-1.5.2.5, SR-1.4.1.1, SR-1.4.1.3
   * RQ-00022-B: SR-1.5.2.5, SR-1.4.1.1, SR-1.4.1.3, SR-1.4.1.7, SR-1.4.1.9 RQ-00022-B: SR-1.5.2.5, SR-1.4.1.1, SR-1.4.1.3 RQ-00022-B: SR-1.4.1.1
   */
  describe('Device alerts', () => {
    it('shows device alerts', async () => {
      render(
        <AlertList
          deviceAlerts={[
            {
              type: ALERT_TYPES.DEVICE,
              id: 'A-001',
              code: DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code,
              deviceId: '40000',
              deviceCode: SENSOR_TYPES.CHEST,
              priority: ALERT_PRIORITY.LOW,
              acknowledged: false,
            },
          ]}
          vitalsAlerts={[]}
        />
      );

      expect(screen.getByTestId('device-alerts-list')).toBeInTheDocument();
      expect(screen.getByTestId('device-alerts-list')).toContainElement(screen.getByText('1'));
      expect(screen.getByTestId('down-full-arrow-icon')).toBeInTheDocument();
      expect(screen.queryByText('Chest Sensor')).not.toBeInTheDocument();
      expect(screen.getAllByText('Sensor out of range')).toHaveLength(1);
      fireEvent.click(screen.getByTestId('down-full-arrow-icon'));
      await waitFor(() => {
        expect(screen.getByText('Chest Sensor')).toBeInTheDocument();
        expect(screen.getAllByText('Sensor out of range')).toHaveLength(2);
      });
      fireEvent.click(screen.getByRole('presentation').firstChild);
      await waitFor(() => {
        expect(screen.queryByText('Chest Sensor')).not.toBeInTheDocument();
        expect(screen.getAllByText('Sensor out of range')).toHaveLength(1);
      });
    });

    /*
     * Requirement IDs: RQ-00022-B: SR-1.4.1.7, SR-1.4.2.1
     */
    it('high priority alerts', async () => {
      render(
        <AlertList
          deviceAlerts={[
            {
              type: ALERT_TYPES.DEVICE,
              id: 'A-001',
              code: DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code,
              deviceId: 'DC-001',
              priority: ALERT_PRIORITY.HIGH,
              acknowledged: false,
              timestamp: '2023-07-20T09:26:01.134',
            },
            {
              type: ALERT_TYPES.DEVICE,
              id: 'A-002',
              code: DEVICE_ALERT_CODES.LOW_SIGNAL_ALERT.code,
              deviceId: 'DC-002',
              priority: ALERT_PRIORITY.MEDIUM,
              acknowledged: false,
              timestamp: '2023-07-20T10:26:01.134',
            },
            {
              type: ALERT_TYPES.DEVICE,
              id: 'A-004',
              code: DEVICE_ALERT_CODES.SENSOR_FAILURE_ALERT.code,
              deviceId: 'DC-001',
              priority: ALERT_PRIORITY.HIGH,
              acknowledged: false,
              timestamp: '2023-07-20T12:26:01.134',
            },
            {
              type: ALERT_TYPES.DEVICE,
              id: 'A-003',
              code: DEVICE_ALERT_CODES.POOR_SKIN_CONTACT_ALERT.code,
              deviceId: 'DC-003',
              priority: ALERT_PRIORITY.LOW,
              acknowledged: false,
              timestamp: '2023-07-20T11:26:01.134',
            },
          ]}
          vitalsAlerts={[]}
        />
      );

      expect(screen.getByTestId('device-alerts-list')).toHaveStyle({ backgroundColor: '#FF4C42' });
      expect(screen.getByTestId('device-alerts-list')).toHaveTextContent('Sensor failure');
    });

    it('medium priority alerts', async () => {
      render(
        <AlertList
          deviceAlerts={[
            {
              type: ALERT_TYPES.DEVICE,
              id: 'A-002',
              code: DEVICE_ALERT_CODES.LEAD_OFF_ALERT.code,
              deviceId: 'DC-002',
              priority: ALERT_PRIORITY.MEDIUM,
              acknowledged: false,
              timestamp: '2023-07-20T11:26:01.134',
            },
            {
              type: ALERT_TYPES.DEVICE,
              id: 'A-002',
              code: DEVICE_ALERT_CODES.LOW_SIGNAL_ALERT.code,
              deviceId: 'DC-002',
              priority: ALERT_PRIORITY.MEDIUM,
              acknowledged: false,
              timestamp: '2023-07-20T09:26:01.134',
            },
            {
              type: ALERT_TYPES.DEVICE,
              id: 'A-003',
              code: DEVICE_ALERT_CODES.POOR_SKIN_CONTACT_ALERT.code,
              deviceId: 'DC-003',
              priority: ALERT_PRIORITY.LOW,
              acknowledged: false,
              timestamp: '2023-07-20T10:26:01.134',
            },
          ]}
          vitalsAlerts={[]}
        />
      );

      expect(screen.getByTestId('device-alerts-list')).toHaveStyle({ backgroundColor: '#F6C905' });
      expect(screen.getByTestId('device-alerts-list')).toHaveTextContent('Lead-off');
    });

    /*
     * Requirement IDs: 	RQ-00022-B: SR-1.4.1.9 RQ-00022-B: SR-1.3.9.3, SR-1.4.1.9 RQ-00022-B: SR-1.3.11.3, SR-1.4.1.9
     */
    it('low priority alerts', async () => {
      render(
        <AlertList
          deviceAlerts={[
            {
              type: ALERT_TYPES.DEVICE,
              id: 'A-003',
              code: DEVICE_ALERT_CODES.POOR_SKIN_CONTACT_ALERT.code,
              deviceId: 'DC-003',
              priority: ALERT_PRIORITY.LOW,
              acknowledged: false,
              timestamp: '2023-07-20T09:26:01.134',
            },
            {
              type: ALERT_TYPES.DEVICE,
              id: 'A-003',
              code: DEVICE_ALERT_CODES.LOW_SIGNAL_ALERT.code,
              deviceId: 'DC-003',
              priority: ALERT_PRIORITY.LOW,
              acknowledged: false,
              timestamp: '2023-07-20T10:26:01.134',
            },
          ]}
          vitalsAlerts={[]}
        />
      );

      expect(screen.getByTestId('device-alerts-list')).toHaveStyle({ backgroundColor: '#75F8FC' });
      expect(screen.getByTestId('device-alerts-list')).toHaveTextContent('Low signal');
    });
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.5.2.5, SR-1.4.1.1, SR-1.4.1.2, SR-1.4.1.4
   */
  describe('Vitals alerts', () => {
    it('shows vitals alerts', async () => {
      render(
        <AlertList
          vitalsAlerts={[
            {
              type: ALERT_TYPES.VITALS,
              id: 'A-001',
              code: VITALS_ALERT_CODES.HR_LOW_AUDIO.code,
              deviceId: '40000',
              deviceCode: SENSOR_CODES.chest,
              priority: ALERT_PRIORITY.LOW,
              acknowledged: false,
              timestamp: '2023-07-20T09:26:01.134',
            },
            {
              type: ALERT_TYPES.VITALS,
              id: 'A-001',
              code: VITALS_ALERT_CODES.HR_HIGH_AUDIO.code,
              deviceId: '40000',
              priority: ALERT_PRIORITY.LOW,
              acknowledged: false,
              timestamp: '2023-07-20T10:26:01.134',
            },
          ]}
          deviceAlerts={[]}
        />
      );

      expect(screen.getByTestId('vitals-alerts-list')).toBeInTheDocument();
      expect(screen.getByTestId('vitals-alerts-list')).toContainElement(screen.getByText('2'));
      expect(screen.getByTestId('down-full-arrow-icon')).toBeInTheDocument();
      expect(screen.getByText('HR High')).toBeInTheDocument();
      expect(screen.queryByText('HR Low')).not.toBeInTheDocument();
      fireEvent.click(screen.getByTestId('down-full-arrow-icon'));
      await waitFor(() => {
        expect(screen.getByText('HR Low')).toBeInTheDocument();
      });
      fireEvent.click(screen.getByRole('presentation').firstChild);
      await waitFor(() => {
        expect(screen.queryByText('HR Low')).not.toBeInTheDocument();
      });
    });

    it('high priority alerts', async () => {
      render(
        <AlertList
          vitalsAlerts={[
            {
              type: ALERT_TYPES.VITALS,
              id: 'A-001',
              code: VITALS_ALERT_CODES.HR_HIGH_AUDIO.code,
              deviceId: '40000',
              priority: ALERT_PRIORITY.HIGH,
              acknowledged: false,
              timestamp: '2023-07-20T09:26:01.134',
            },
            {
              type: ALERT_TYPES.VITALS,
              id: 'A-002',
              code: VITALS_ALERT_CODES.SYS_HIGH_AUDIO.code,
              deviceId: '40000',
              priority: ALERT_PRIORITY.HIGH,
              acknowledged: false,
              timestamp: '2023-07-20T09:26:07.934',
            },
            {
              type: ALERT_TYPES.VITALS,
              id: 'A-002',
              code: VITALS_ALERT_CODES.RR_HIGH_AUDIO.code,
              deviceId: '40000',
              priority: ALERT_PRIORITY.MEDIUM,
              acknowledged: false,
              timestamp: '2023-07-20T09:26:07.934',
            },
            {
              type: ALERT_TYPES.VITALS,
              id: 'A-003',
              code: VITALS_ALERT_CODES.SPO2_HIGH_AUDIO.code,
              deviceId: '40000',
              priority: ALERT_PRIORITY.LOW,
              acknowledged: false,
              timestamp: '2023-07-20T09:26:07.934',
            },
          ]}
          deviceAlerts={[]}
        />
      );

      expect(screen.getByTestId('vitals-alerts-list')).toHaveStyle({ backgroundColor: '#FF4C42' });
      expect(screen.getByTestId('vitals-alerts-list')).toHaveTextContent('NIBP SYS High');
    });

    it('medium priority alerts', async () => {
      render(
        <AlertList
          vitalsAlerts={[
            {
              type: ALERT_TYPES.VITALS,
              id: 'A-002',
              code: VITALS_ALERT_CODES.RR_HIGH_AUDIO.code,
              deviceId: '40000',
              priority: ALERT_PRIORITY.MEDIUM,
              acknowledged: false,
              timestamp: '2023-07-20T09:26:01.134',
            },
            {
              type: ALERT_TYPES.VITALS,
              id: 'A-003',
              code: VITALS_ALERT_CODES.HR_HIGH_AUDIO.code,
              deviceId: '40000',
              priority: ALERT_PRIORITY.LOW,
              acknowledged: false,
              timestamp: '2023-07-20T09:26:07.934',
            },
            {
              type: ALERT_TYPES.VITALS,
              id: 'A-004',
              code: VITALS_ALERT_CODES.DIA_HIGH_AUDIO.code,
              deviceId: '40000',
              priority: ALERT_PRIORITY.MEDIUM,
              acknowledged: false,
              timestamp: '2023-07-20T09:26:16.024',
            },
          ]}
          deviceAlerts={[]}
        />
      );

      expect(screen.getByTestId('vitals-alerts-list')).toHaveStyle({ backgroundColor: '#F6C905' });
      expect(screen.getByTestId('vitals-alerts-list')).toHaveTextContent('NIBP DIA High');
    });

    it('low priority alerts', async () => {
      render(
        <AlertList
          vitalsAlerts={[
            {
              type: ALERT_TYPES.VITALS,
              id: 'A-003',
              code: VITALS_ALERT_CODES.RR_LOW_AUDIO.code,
              deviceId: '40000',
              priority: ALERT_PRIORITY.LOW,
              acknowledged: false,
              timestamp: '2023-07-20T09:26:48.035',
            },
            {
              type: ALERT_TYPES.VITALS,
              id: 'A-003',
              code: VITALS_ALERT_CODES.DIA_HIGH_AUDIO.code,
              deviceId: '40000',
              priority: ALERT_PRIORITY.LOW,
              acknowledged: false,
              timestamp: '2023-07-20T09:26:16.024',
            },
          ]}
          deviceAlerts={[]}
        />
      );

      expect(screen.getByTestId('vitals-alerts-list')).toHaveStyle({ backgroundColor: '#75F8FC' });
      expect(screen.getByTestId('vitals-alerts-list')).toHaveTextContent('RR Low');
    });
  });
});
