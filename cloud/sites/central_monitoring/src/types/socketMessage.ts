import { ALERT_PRIORITY, ALERT_TYPES } from '@/utils/metricCodes';
import { RESPONSE_STATUS } from '@/utils/status';
import { SensorStatus } from './sensor';

export interface SocketWorkerMessage {
  status: RESPONSE_STATUS;
  pid?: string;
  code?: string;
  deviceId?: string;
  upperLimit?: string;
  lowerLimit?: string;
  newConnectionStatus?: boolean;
  bedId?: string;
  monitorId?: string;
  deviceCode?: string;
  active?: boolean;
  alertPriority?: ALERT_PRIORITY;
  type?: ALERT_TYPES | null;
  alertId?: string;
  timestamp?: number | string;
  samples?: string | number | (number | null)[] | boolean | null;
  sensorId?: string;
  unitCode?: string;
  isPatientMonitor?: boolean;
}

export interface SensorDataSocketWorkerMessage extends SocketWorkerMessage {
  samples: number | SensorStatus | null;
  sensorId: string;
}

export interface RawSocketMessagePayload extends AlertSocketMessagePayload {
  connection_status?: string;
  device?: DeviceSocketMessagePayload;
  patient?: PatientSocketMessagePayload;
  message_id?: string;
  samples?: string[];
  unit_code?: string;
  audio_enabled?: boolean;
  audio_pause_enabled?: boolean;
}

interface RawSocketMessageEventState {
  id?: string;
  code?: string;
  device?: DeviceSocketMessagePayload;
  patient?: PatientSocketMessagePayload;
  patient_id?: string;
  primary_identifier?: string;
  patient_primary_identifier?: string;
  gateway_id?: string;
  device_id?: string;
  upper_limit?: string;
  lower_limit?: string;
  model_number?: string;
}

export interface RawSocketMessage {
  message_id?: string;
  payload?: RawSocketMessagePayload;
  event_type: string;
  event_state?: RawSocketMessageEventState;
  previous_state?: RawSocketMessageEventState;
  entity_id?: string;
}

interface DeviceSocketMessagePayload {
  primary_identifier: string;
  name: string;
  gateway_id: string;
  location_id?: string;
  device_code: string;
  connected_sensors: never[];
  alerts: AlertSocketMessagePayload[];
}

export interface PatientSocketMessagePayload {
  alerts: AlertSocketMessagePayload[];
  id?: string;
}

export interface AlertSocketMessagePayload {
  patient_primary_identifier?: string;
  patient_id?: string;
  active?: string;
  code?: string;
  device_code?: string;
  priority?: string;
  determination_time?: string;
  device_primary_identifier?: string;
}
