import { BedsideAudioAlarmStatus, DeviceAlert, ServerSideDeviceAlerts } from '@/types/alerts';
import {
  PatientMonitor,
  ServerSidePatientMonitor,
  ServerSidePatientMonitorConfig,
  ServerSideVitalsRange,
  VitalsRange,
} from '@/types/patientMonitor';
import { SENSOR_TYPES, Sensor, ServerSideSensor } from '@/types/sensor';
import { getDeviceAlert } from '@/utils/alertUtils';
import { ALERT_TYPES, SUPPORTED_ALERT_CODES } from '@/utils/metricCodes';
import moment from 'moment';

const parseVitalRanges = (ranges: ServerSideVitalsRange[]): VitalsRange[] =>
  ranges.map((range) => ({
    id: range.id,
    code: range.code,
    upperLimit: range.upper_limit,
    lowerLimit: range.lower_limit,
    alertConditionEnabled: range.alert_condition_enabled,
  }));

const parseServerDeviceAlerts = (
  alerts: ServerSideDeviceAlerts[],
  deviceCode: string
): DeviceAlert[] =>
  alerts
    .filter((alert) => SUPPORTED_ALERT_CODES.includes(alert.code))
    .map((alert) => ({
      type: ALERT_TYPES.DEVICE,
      id: alert.id,
      code: alert.code,
      deviceCode: deviceCode,
      priority: alert.priority,
      acknowledged: false,
      timestamp: `${moment(alert.createdAt).toISOString()}`,
      waveformMessage: getDeviceAlert(alert.code, deviceCode as SENSOR_TYPES)?.waveformMessage,
    }));

const parseServerMonitorBedsideAlarmStatus = (
  patientMonitorConfig?: ServerSidePatientMonitorConfig
): BedsideAudioAlarmStatus => {
  if (patientMonitorConfig) {
    if (!patientMonitorConfig.audio_enabled) return BedsideAudioAlarmStatus.OFF;
    if (patientMonitorConfig.audio_pause_enabled) return BedsideAudioAlarmStatus.PAUSED;
  }
  return BedsideAudioAlarmStatus.ACTIVE;
};

export const parseServerSensors = (sensors: ServerSideSensor[]) => {
  const parsedSensors: Sensor[] = [];
  const alertsPerMonitor: Record<string, DeviceAlert[]> = {};

  sensors.forEach((sensor) => {
    if (sensor.gateway_id) {
      const patientMonitorId = sensor.gateway_id;
      if (!alertsPerMonitor[patientMonitorId]) alertsPerMonitor[patientMonitorId] = [];
      parsedSensors.push({
        id: sensor.id,
        primaryIdentifier: sensor.primary_identifier,
        title: sensor.name,
        type: sensor.device_code as SENSOR_TYPES,
        patientMonitorId,
      });
      alertsPerMonitor[patientMonitorId] = alertsPerMonitor[patientMonitorId].concat(
        sensor.alerts
          ? parseServerDeviceAlerts(sensor.alerts, sensor.device_code as SENSOR_TYPES)
          : []
      );
    }
  });

  return { sensors: parsedSensors, alertsPerMonitor };
};

export const parseServerPatientMonitors = (
  patientMonitors: ServerSidePatientMonitor[]
): PatientMonitor[] =>
  patientMonitors.map((monitor) => ({
    id: monitor.id,
    monitorId: monitor.primary_identifier,
    deviceCode: monitor.device_code,
    assignedBedId: monitor.location_id,
    vitalRanges: monitor.vital_ranges ? parseVitalRanges(monitor.vital_ranges) : [],
    alerts: monitor.alerts ? parseServerDeviceAlerts(monitor.alerts, monitor.device_code) : [],
    bedsideAudioAlarmStatus: parseServerMonitorBedsideAlarmStatus(monitor.config),
  }));
