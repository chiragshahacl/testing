import { DeviceAlert } from '@/types/alerts';
import { TECHNICAL_ALERT_MAPPING, TECHNICAL_ALERT_TYPE } from '@/utils/alertUtils';
import { useMemo } from 'react';

/**
 * Calculates and memoizes the technical alerts from the device alerts
 * @param deviceAlerts List of current device alerts
 */
const useTechnicalAlerts = (deviceAlerts: DeviceAlert[]): Record<TECHNICAL_ALERT_TYPE, boolean> =>
  useMemo(() => {
    const newTechnicalAlerts = Object.fromEntries(
      Object.values(TECHNICAL_ALERT_TYPE).map((type) => [type, false])
    ) as Record<TECHNICAL_ALERT_TYPE, boolean>;

    deviceAlerts.forEach((deviceAlert) => {
      TECHNICAL_ALERT_MAPPING.forEach(({ technicalAlertTypes, deviceCode, alertCodes }) => {
        if (deviceAlert.deviceCode === deviceCode && alertCodes.includes(deviceAlert.code)) {
          technicalAlertTypes.forEach(
            (technicalAlertType) => (newTechnicalAlerts[technicalAlertType] = true)
          );
        }
      });
    });

    return newTechnicalAlerts;
  }, [deviceAlerts]);

export default useTechnicalAlerts;
