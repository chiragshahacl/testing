import { DeviceAlert, ServerSideDeviceAlerts } from './alerts';

/* eslint-disable camelcase */
export interface ServerSideSensor {
  id: string;
  name?: string;
  primary_identifier: string;
  gateway_id?: string;
  device_code?: string;
  alerts?: ServerSideDeviceAlerts[];
}

export enum SensorStatus {
  CONNECTED = 'CONNECTED',
  CONNECTION_LOST = 'CONNECTION_LOST',
}

export interface Sensor {
  id: string;
  primaryIdentifier: string;
  type: SENSOR_TYPES;
  title?: string;
  patientMonitorId: string;
}

export interface SensorQueryReturn {
  sensors: Sensor[];
  alertsPerMonitor: Record<string, DeviceAlert[]>;
}

export const RANGE_TYPES = {
  HR: 'hr',
  RR: 'rr',
};

export const SENSOR_CODES = {
  chest: '40000',
  adam: '40002',
  limb: '40001',
  nonin: '40003',
  bp: '40004',
};

export enum SENSOR_TYPES {
  CHEST = 'ANNE Chest',
  ADAM = 'ADAM',
  LIMB = 'ANNE Limb',
  NONIN = 'Nonin 3150',
  BP = 'Viatom BP monitor',
  THERMOMETER = 'DMT Thermometer',
  PATIENT_MONITOR = 'Patient Monitor',
}
