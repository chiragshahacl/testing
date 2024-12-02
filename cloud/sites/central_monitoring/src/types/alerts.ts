import { ALERT_PRIORITY, ALERT_TYPES } from '@/utils/metricCodes';
import { DisplayVitalsRange } from './patientMonitor';
import { SENSOR_TYPES } from './sensor';

export interface ServerAlert {
  id: string;
  category: string;
  code: string;
  deviceCode: string;
  effectiveDt: string;
  valueNumber: number;
  valueText: ALERT_PRIORITY;
}

export interface ServerSidePatientAlert {
  primaryIdentifier: string;
  alerts: ServerAlert[];
}

export interface ServerSideDeviceAlerts {
  id: string;
  code: string;
  priority: ALERT_PRIORITY;
  createdAt: string;
}

export interface Alert {
  type: ALERT_TYPES;
  id: string;
  code: string;
  deviceCode: string;
  priority: ALERT_PRIORITY;
  acknowledged: boolean;
  timestamp: string;
  waveformMessage?: string;
}

export interface DeviceAlert extends Alert {
  type: ALERT_TYPES.DEVICE;
}
export interface VitalsAlert extends Alert {
  type: ALERT_TYPES.VITALS;
}

export interface PatientAlerts {
  patientId: string;
  alerts: Alert[];
}

export type AlertMetadata = {
  code: string;
  message: string;
  waveformMessage?: string;
  devices?: SENSOR_TYPES[];
};

export type AlertThresholds = Record<string, Record<string, DisplayVitalsRange>>;

export type AlertMetadataMapping = Record<string, AlertMetadata>;

export type AlarmRecord = {
  type: string;
  date: string;
  time: string;
  priority: ALERT_PRIORITY;
  message: string;
  duration: string;
};

export enum BedsideAudioAlarmStatus {
  PAUSED = 'PAUSED',
  OFF = 'OFF',
  ACTIVE = 'ACTIVE',
}
