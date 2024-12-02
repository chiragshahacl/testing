import { usePatientMonitors } from '@/api/usePatientMonitors';
import useThrottledState from '@/hooks/useThrottledState';
import { BedsideAudioAlarmStatus } from '@/types/alerts';
import { Metrics } from '@/types/metrics';
import { PatientPrimaryID } from '@/types/patient';
import { SENSOR_TYPES } from '@/types/sensor';
import { CONTINUOUS_METRICS, METRIC_INTERNAL_CODES, METRIC_SENSOR_MAP } from '@/utils/metricCodes';
import { cloneDeep } from 'lodash';
import { createContext, useEffect } from 'react';

interface MetricsContextProps {
  children: React.ReactNode;
}

interface MetricsContextType {
  metrics: Record<PatientPrimaryID, Metrics>;
  sensorMetrics: Record<string, Metrics>;
  bedsideStatus: Record<string, BedsideAudioAlarmStatus>;
  postNewMetric: (
    pid: PatientPrimaryID,
    metricCode: string,
    value: string | number | null,
    unit?: string,
    timestamp?: string
  ) => void;
  postNewSensorMetric: (
    sensorId: string,
    metricCode: string,
    value: string | number | null,
    unit?: string,
    timestamp?: string
  ) => void;
  postNewBedsideStatus: (patientMonitorId: string, newStatus: BedsideAudioAlarmStatus) => void;
  resetContinuousMetricsForDeviceForPatient: (
    deviceType: SENSOR_TYPES,
    pid: PatientPrimaryID
  ) => void;
  resetMetrics: () => void;
}

// Rate limit in milliseconds at which the metrics' state will be updated
const METRICS_RATE_LIMIT = 200;

export const MetricsData = createContext<MetricsContextType | null>(null);

/**
 * @description Manages all aspects regarding to vitals and sensors metrics throughout CMS.
 * This does NOT include Waveform data, but all other metrics.
 * Values provided are current metrics and methods for updating metric values. Includes:
 * metrics - Record. Contains latest values received for all metrics by patient
 * postNewMetric - Method for adding a new metric value for a specific patient
 * sensorMetrics - Record. Contains latest values received for all sensor metrics
 *      by sensor id
 * postNewSensorMetric - Method for adding a new sensor metric value for a specific sensor
 * resetMetrics - Method for resetting all vitals and sensor metrics for all patients and
 *      sensors
 */
const MetricsContext = ({ children }: MetricsContextProps) => {
  const [metrics, setMetrics] = useThrottledState<Record<PatientPrimaryID, Metrics>>(
    {},
    METRICS_RATE_LIMIT
  );
  const [sensorMetrics, setSensorMetrics] = useThrottledState<Record<string, Metrics>>(
    {},
    METRICS_RATE_LIMIT
  );
  const [bedsideStatus, setBedsideStatus] = useThrottledState<
    Record<string, BedsideAudioAlarmStatus>
  >({}, METRICS_RATE_LIMIT);
  const patientMonitors = usePatientMonitors();

  const resetContinuousMetricsForDeviceForPatient = (
    deviceType: SENSOR_TYPES,
    pid: PatientPrimaryID
  ) => {
    const emptyMetrics: Partial<Record<METRIC_INTERNAL_CODES, undefined>> = {};
    CONTINUOUS_METRICS.forEach((metric) => {
      if (METRIC_SENSOR_MAP[metric] && METRIC_SENSOR_MAP[metric].includes(deviceType)) {
        emptyMetrics[metric] = undefined;
      }
    });

    setMetrics((previousMetrics) => ({
      ...previousMetrics,
      [pid]: Object.assign({}, previousMetrics[pid], emptyMetrics),
    }));
  };

  const resetMetrics = () => {
    setMetrics({});
    setSensorMetrics({});
  };

  const postNewMetric = (
    pid: PatientPrimaryID,
    metricCode: string,
    value: string | number | null,
    unit?: string,
    timestamp?: string
  ) => {
    setMetrics((previousMetrics) => ({
      ...previousMetrics,
      [pid]: Object.assign({}, previousMetrics[pid], {
        [metricCode]: {
          value,
          unit,
          timestamp,
        },
      }),
    }));
  };

  const postNewSensorMetric = (
    sensorId: string,
    metricCode: string,
    value: string | number | null,
    unit?: string,
    timestamp?: string
  ) => {
    setSensorMetrics((previousMetrics) => ({
      ...previousMetrics,
      [sensorId]: Object.assign({}, previousMetrics[sensorId], {
        [metricCode]: {
          value,
          unit,
          timestamp,
        },
      }),
    }));
  };

  const postNewBedsideStatus = (patientMonitorId: string, newStatus?: BedsideAudioAlarmStatus) => {
    setBedsideStatus((previousStatus) => {
      if (newStatus) return { ...previousStatus, [patientMonitorId]: newStatus };
      else {
        const newBedsideStatus = cloneDeep(previousStatus);
        delete newBedsideStatus[patientMonitorId];
        return newBedsideStatus;
      }
    });
  };

  useEffect(() => {
    if (patientMonitors.data) {
      const newBedsideStatus = cloneDeep(bedsideStatus);
      patientMonitors.data.forEach((patientMonitor) => {
        if (patientMonitor.bedsideAudioAlarmStatus)
          newBedsideStatus[patientMonitor.monitorId] = patientMonitor.bedsideAudioAlarmStatus;
        else if (newBedsideStatus[patientMonitor.monitorId])
          delete newBedsideStatus[patientMonitor.monitorId];
      });
      setBedsideStatus(newBedsideStatus);
    } else {
      setBedsideStatus({});
    }
  }, [patientMonitors.data]);

  return (
    <MetricsData.Provider
      value={{
        metrics,
        postNewMetric,
        sensorMetrics,
        postNewSensorMetric,
        bedsideStatus,
        postNewBedsideStatus,
        resetContinuousMetricsForDeviceForPatient,
        resetMetrics,
      }}
    >
      {children}
    </MetricsData.Provider>
  );
};

export default MetricsContext;
