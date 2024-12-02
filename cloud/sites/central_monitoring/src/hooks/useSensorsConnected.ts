import { Sensor } from '@/types/sensor';
import { METRIC_INTERNAL_CODES } from '@/utils/metricCodes';
import { checkSensorConnection } from '@/utils/sensorUtils';
import { useMemo } from 'react';

/**
 * Calculates and memoizes for each vitals metric if there is a currently active sensor
 * that handles the specific metric
 * @param activeSensors List of sensors that are currently connected for a bed
 * @param hasActivePatientSession Boolean that indicates if there is an active patient session
 */
const useSensorsConnected = (
  activeSensors: Sensor[],
  hasActivePatientSession = false
): Record<METRIC_INTERNAL_CODES, boolean> =>
  useMemo(
    () => ({
      [METRIC_INTERNAL_CODES.HR]: checkSensorConnection(activeSensors, METRIC_INTERNAL_CODES.HR),
      [METRIC_INTERNAL_CODES.SPO2]: checkSensorConnection(
        activeSensors,
        METRIC_INTERNAL_CODES.SPO2
      ),
      [METRIC_INTERNAL_CODES.PR]: checkSensorConnection(activeSensors, METRIC_INTERNAL_CODES.PR),
      [METRIC_INTERNAL_CODES.PI]: checkSensorConnection(activeSensors, METRIC_INTERNAL_CODES.PI),
      [METRIC_INTERNAL_CODES.RR_METRIC]: checkSensorConnection(
        activeSensors,
        METRIC_INTERNAL_CODES.RR_METRIC
      ),
      [METRIC_INTERNAL_CODES.PULSE]: checkSensorConnection(
        activeSensors,
        METRIC_INTERNAL_CODES.PULSE
      ),
      [METRIC_INTERNAL_CODES.NIBP]: checkSensorConnection(
        activeSensors,
        METRIC_INTERNAL_CODES.NIBP
      ),
      [METRIC_INTERNAL_CODES.BODY_TEMP]: checkSensorConnection(
        activeSensors,
        METRIC_INTERNAL_CODES.BODY_TEMP
      ),
      [METRIC_INTERNAL_CODES.CHEST_TEMP]: checkSensorConnection(
        activeSensors,
        METRIC_INTERNAL_CODES.CHEST_TEMP
      ),
      [METRIC_INTERNAL_CODES.LIMB_TEMP]: checkSensorConnection(
        activeSensors,
        METRIC_INTERNAL_CODES.LIMB_TEMP
      ),
      [METRIC_INTERNAL_CODES.FALLS]: checkSensorConnection(
        activeSensors,
        METRIC_INTERNAL_CODES.FALLS
      ),
      [METRIC_INTERNAL_CODES.POSITION]: checkSensorConnection(
        activeSensors,
        METRIC_INTERNAL_CODES.POSITION
      ),
      [METRIC_INTERNAL_CODES.ECG]:
        hasActivePatientSession && checkSensorConnection(activeSensors, METRIC_INTERNAL_CODES.ECG),
      [METRIC_INTERNAL_CODES.RR]:
        hasActivePatientSession && checkSensorConnection(activeSensors, METRIC_INTERNAL_CODES.RR),
      [METRIC_INTERNAL_CODES.PLETH]:
        hasActivePatientSession &&
        checkSensorConnection(activeSensors, METRIC_INTERNAL_CODES.PLETH),
      [METRIC_INTERNAL_CODES.DIA]: false,
      [METRIC_INTERNAL_CODES.SYS]: false,
      [METRIC_INTERNAL_CODES.MAP]: false,
      [METRIC_INTERNAL_CODES.POSITION_DURATION]: false,
      [METRIC_INTERNAL_CODES.BODY_ANGLE]: false,
    }),
    [activeSensors, hasActivePatientSession]
  );

export default useSensorsConnected;
