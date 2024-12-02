import { BedsideAudioAlarmStatus, DeviceAlert, ServerSideDeviceAlerts } from '@/types/alerts';

export interface DisplayVitalsRange {
  upperLimit: string;
  lowerLimit: string;
  alertConditionEnabled?: boolean;
}

export interface ServerSideVitalsRange {
  id: string;
  code: string;
  upper_limit: number;
  lower_limit: number;
  alert_condition_enabled?: boolean;
}

export interface VitalsRange {
  id: string;
  code: string;
  upperLimit: number;
  lowerLimit: number;
  alertConditionEnabled?: boolean;
}

export interface PatientMonitor {
  id: string;
  monitorId: string;
  assignedBedId: string | null;
  deviceCode: string | null;
  vitalRanges?: VitalsRange[];
  alerts: DeviceAlert[];
  bedsideAudioAlarmStatus?: BedsideAudioAlarmStatus;
}

export interface BedMonitorAssociation {
  bed_id: string | null;
  device_id: string;
}

export interface ServerSidePatientMonitorConfig {
  audio_pause_enabled: boolean;
  audio_enabled: boolean;
}

export interface ServerSidePatientMonitor {
  id: string;
  primary_identifier: string;
  name: string;
  location_id: string | null;
  gateway_id: string | null;
  device_code: string;
  vital_ranges?: ServerSideVitalsRange[];
  alerts?: ServerSideDeviceAlerts[];
  config?: ServerSidePatientMonitorConfig;
}

export interface BedsDisplayGroup {
  screenId: string;
  beds: string[];
  timestamp: number;
}
