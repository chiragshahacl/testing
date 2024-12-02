import { AlertMetadataMapping } from '@/types/alerts';
import { UnitCode } from '@/types/codes';
import { SENSOR_TYPES } from '@/types/sensor';
import { get } from 'lodash';

export enum METRIC_INTERNAL_CODES {
  ECG = 'ecg',
  HR = 'hr',
  SYS = 'sys',
  DIA = 'dia',
  NIBP = 'nibp',
  PLETH = 'pleth',
  PULSE = 'pulse',
  PR = 'pr',
  RR = 'rr',
  RR_METRIC = 'rrMetric',
  BODY_TEMP = 'bodyTemp',
  LIMB_TEMP = 'limbTemp',
  CHEST_TEMP = 'chestTemp',
  SPO2 = 'spo2',
  PI = 'pi',
  FALLS = 'falls',
  POSITION = 'position',
  POSITION_DURATION = 'positionDuration',
  MAP = 'map',
  BODY_ANGLE = 'bodyAngle',
}

export const METRIC_CODES: Record<string, Record<string, string>> = {
  '131328': { all: METRIC_INTERNAL_CODES.ECG },
  '147844': { all: METRIC_INTERNAL_CODES.HR },
  '150021': { all: METRIC_INTERNAL_CODES.SYS },
  '150022': { all: METRIC_INTERNAL_CODES.DIA },
  '150452': { all: METRIC_INTERNAL_CODES.PLETH },
  '149540': {
    'Viatom BP monitor': METRIC_INTERNAL_CODES.PULSE,
    'ANNE Limb': METRIC_INTERNAL_CODES.PR,
    'Nonin 3150': METRIC_INTERNAL_CODES.PR,
  },
  '151780': { all: METRIC_INTERNAL_CODES.RR },
  '151556': { all: METRIC_INTERNAL_CODES.RR_METRIC },
  '150364': { all: METRIC_INTERNAL_CODES.BODY_TEMP },
  '150388': {
    // Limb and chest temp use the same code, but for different devices
    'ANNE Limb': METRIC_INTERNAL_CODES.LIMB_TEMP,
    'ANNE Chest': METRIC_INTERNAL_CODES.CHEST_TEMP,
    ADAM: METRIC_INTERNAL_CODES.CHEST_TEMP,
  },
  '150316': { all: METRIC_INTERNAL_CODES.SPO2 },
  '150488': { all: METRIC_INTERNAL_CODES.PI },
  '192512': { all: METRIC_INTERNAL_CODES.FALLS },
  '192513': { all: METRIC_INTERNAL_CODES.POSITION },
  '192520': { all: METRIC_INTERNAL_CODES.POSITION_DURATION },
  '150035': { all: METRIC_INTERNAL_CODES.MAP },
  '192530': { all: METRIC_INTERNAL_CODES.BODY_ANGLE },
};

export const getMetricCode = (wsCode: string, deviceCode?: string): string => {
  if (!deviceCode) return METRIC_CODES[wsCode]?.['all'];
  return METRIC_CODES[wsCode]?.[deviceCode] ?? METRIC_CODES[wsCode]?.['all'];
};

export enum ALERT_TYPES {
  VITALS = 'vitals',
  DEVICE = 'device',
}

export enum POSITION_TYPES {
  SUPINE = 'SUPINE',
  PRONE = 'PRONE',
  UPRIGHT = 'UPRIGHT',
  RIGHTL = 'RIGHT',
  LEFTL = 'LEFT',
}

export enum ALERT_PRIORITY {
  HIGH = 'HI',
  MEDIUM = 'ME',
  LOW = 'LO',
  INTERNAL = 'INTERNAL', // Alerts handled internally by CMS
}

export const ALERT_PRIORITY_LABEL: Partial<Record<ALERT_PRIORITY, string>> = {
  [ALERT_PRIORITY.HIGH]: 'High',
  [ALERT_PRIORITY.LOW]: 'Low',
  [ALERT_PRIORITY.MEDIUM]: 'Medium',
};

const codesByMetric: Partial<Record<METRIC_INTERNAL_CODES, string>> = Object.entries(
  METRIC_CODES
).reduce((prev, entry) => {
  const a = Object.values(entry[1]);
  const b: Record<string, string> = { ...prev };
  a.forEach((val) => {
    b[val] = entry[0];
  });
  return b;
}, {});

export const WS_CODES: Record<string, string> = {
  // Metric values
  HR: get(codesByMetric, METRIC_INTERNAL_CODES.HR, ''),
  ECG: get(codesByMetric, METRIC_INTERNAL_CODES.ECG, ''),
  SYS: get(codesByMetric, METRIC_INTERNAL_CODES.SYS, ''),
  DIA: get(codesByMetric, METRIC_INTERNAL_CODES.DIA, ''),
  MAP: get(codesByMetric, METRIC_INTERNAL_CODES.MAP, ''),
  SPO2: get(codesByMetric, METRIC_INTERNAL_CODES.SPO2, ''),
  PLETH: get(codesByMetric, METRIC_INTERNAL_CODES.PLETH, ''),
  RR: get(codesByMetric, METRIC_INTERNAL_CODES.RR, ''),
  POSITION: get(codesByMetric, METRIC_INTERNAL_CODES.POSITION, ''), // This one is the one for position type, not duration
  // Non-metric values
  DEVICE_BATTERY: '65577',
  DEVICE_BATTERY_STATUS: '65577-S',
  DEVICE_SIGNAL: '192522',
  DEVICE_STATUS: '192523',
};

export const RANGES_CODES = {
  HR: '258418',
  RR: '258419',
  SYS: '258421',
  DIA: '258422',
  SPO2: '258420',
  PR: '258427',
  TEMPERATURE_SKIN: '258424',
  TEMPERATURE_BODY: '258425',
  FALLS: '8574701',
  POSITION_DURATION: '258426',
};

export const UNIT_CODES: Record<string, UnitCode> = {
  '262144': {
    name: 'NO_UNIT',
    display: '',
  },
  '264864': {
    name: 'BEATS_PER_MINUTE',
    display: 'bpm',
  },
  '264928': {
    name: 'BREATHS_PER_MINUTE',
    display: 'brpm',
  },
  '266560': {
    name: 'FAHRENHEIT',
    display: '°F',
  },
  '268192': {
    name: 'CELSIUS',
    display: '°C',
  },
  '264352': {
    name: 'TIME',
    display: 'minutes',
  },
  '266436': {
    name: 'MILIVOLT',
    display: 'mV',
  },
  '268768': {
    name: 'G_FORCE',
    display: 'g-force',
  },
  '262688': {
    name: 'PERCENTAGE',
    display: '%',
  },
  '266325': {
    name: 'PICO_AMPERE',
    display: 'pA',
  },
  '266016': {
    name: 'MERCURY_MILIMETRES',
    display: 'mmHg',
  },
  '262880': {
    name: 'ANGLE',
    display: '°',
  },
};

export const EVENT_CODES = {
  DEVICE_CREATED_EVENT: 'DEVICE_CREATED_EVENT',
  DEVICE_DELETED_EVENT: 'DEVICE_DELETED_EVENT',
  DEVICE_UPDATED_EVENT: 'DEVICE_UPDATED_EVENT',
  BED_CREATED_EVENT: 'BED_CREATED_EVENT',
  BED_DELETED_EVENT: 'BED_DELETED_EVENT',
  BED_UPDATED_EVENT: 'BED_UPDATED_EVENT',
  BED_ASSIGNED_TO_GROUP_EVENT: 'BED_ASSIGNED_TO_GROUP_EVENT',
  BED_REMOVED_FROM_GROUP_EVENT: 'BED_REMOVED_FROM_GROUP_EVENT',
  BED_GROUP_DELETED_EVENT: 'BED_GROUP_DELETED_EVENT',
  BED_GROUP_UPDATED_EVENT: 'BED_GROUP_UPDATED_EVENT',
  BED_GROUP_CREATED_EVENT: 'BED_GROUP_CREATED_EVENT',
  PATIENT_ENCOUNTER_STARTED: 'PATIENT_ENCOUNTER_STARTED',
  PATIENT_ENCOUNTER_PLANNED: 'PATIENT_ENCOUNTER_PLANNED',
  PATIENT_ENCOUNTER_COMPLETED: 'PATIENT_ENCOUNTER_COMPLETED',
  PATIENT_ENCOUNTER_CANCELLED: 'PATIENT_ENCOUNTER_CANCELLED',
  ASSIGN_DEVICE_LOCATION_EVENT: 'ASSIGN_DEVICE_LOCATION_EVENT',
  UNASSIGN_DEVICE_LOCATION_EVENT: 'UNASSIGN_DEVICE_LOCATION_EVENT',
  OBSERVATION_CREATED_EVENT: 'OBSERVATION_CREATED_EVENT',
  OBSERVATION_DELETED_EVENT: 'OBSERVATION_DELETED_EVENT',
  DEVICE_ALERT_CREATED: 'DEVICE_ALERT_CREATED',
  DEVICE_ALERT_DELETED: 'DEVICE_ALERT_DELETED',
  MULTIPLE_DEVICE_ALERTS_UPDATED: 'MULTIPLE_DEVICE_ALERTS_UPDATED',
  MULTIPLE_OBSERVATIONS_UPDATED: 'MULTIPLE_OBSERVATIONS_UPDATED',
  ALERT_DEACTIVATED_EVENT: 'ALERT_DEACTIVATED_EVENT',
  VITAL_RANGE_CREATED_EVENT: 'VITAL_RANGE_CREATED_EVENT',
  PM_CONNECTION_STATUS_REPORT: 'PM_CONNECTION_STATUS_REPORT',
  PM_CONFIGURATION_UPDATED: 'PM_CONFIGURATION_UPDATED',
  PATIENT_SESSION_CLOSED_EVENT: 'PATIENT_SESSION_CLOSED_EVENT',
};

export const DEVICE_CODES = {
  ANNE_CHEST: {
    name: 'Chest Sensor',
    type: SENSOR_TYPES.CHEST,
  },
  ANNE_LIMB: {
    name: 'Limb Sensor',
    type: SENSOR_TYPES.LIMB,
  },
  ADAM: {
    name: 'ADAM Sensor',
    type: SENSOR_TYPES.ADAM,
  },
  NONIN_3150: {
    name: 'Nonin',
    type: SENSOR_TYPES.NONIN,
  },
  VIATOM_BP: {
    name: 'Viatom BP',
    type: SENSOR_TYPES.BP,
  },
  JOYTECH_THERMOMETER: {
    name: 'Thermometer',
    type: SENSOR_TYPES.THERMOMETER,
  },
  PATIENT_MONITOR: {
    name: 'Patient Monitor',
    type: SENSOR_TYPES.PATIENT_MONITOR,
  },
};

export const AUDIO_ALERT_CODES: AlertMetadataMapping = {
  HR_LOW_AUDIO: {
    code: '258053',
    message: 'HR Low',
  },
  HR_HIGH_AUDIO: {
    code: '258049',
    message: 'HR High',
  },
  RR_LOW_AUDIO: {
    code: '258057',
    message: 'RR Low',
  },
  RR_HIGH_AUDIO: {
    code: '258061',
    message: 'RR High',
  },
  SPO2_LOW_AUDIO: {
    code: '258065',
    message: 'SpO2 Low',
  },
  SPO2_HIGH_AUDIO: {
    code: '258069',
    message: 'SpO2 High',
  },
  PR_LOW_AUDIO: {
    code: '258177',
    message: 'PR Low',
  },
  PR_HIGH_AUDIO: {
    code: '258181',
    message: 'PR High',
  },
  SYS_LOW_AUDIO: {
    code: '258073',
    message: 'NIBP SYS Low',
  },
  SYS_HIGH_AUDIO: {
    code: '258077',
    message: 'NIBP SYS High',
  },
  DIA_LOW_AUDIO: {
    code: '258081',
    message: 'NIBP DIA Low',
  },
  DIA_HIGH_AUDIO: {
    code: '258085',
    message: 'NIBP DIA High',
  },
  BODY_TEMP_LOW_AUDIO: {
    code: '258161',
    message: 'Body Temp Low',
  },
  BODY_TEMP_HIGH_AUDIO: {
    code: '258165',
    message: 'Body Temp High',
  },
  CHEST_TEMP_LOW_AUDIO: {
    code: '258153',
    message: 'Chest Skin Temp Low',
    devices: [SENSOR_TYPES.ADAM, SENSOR_TYPES.CHEST],
  },
  CHEST_TEMP_HIGH_AUDIO: {
    code: '258157',
    message: 'Chest Skin Temp High',
    devices: [SENSOR_TYPES.ADAM, SENSOR_TYPES.CHEST],
  },
  LIMB_TEMP_LOW_AUDIO: {
    code: '258153',
    message: 'Limb Skin Temp Low',
    devices: [SENSOR_TYPES.LIMB],
  },
  LIMB_TEMP_HIGH_AUDIO: {
    code: '258157',
    message: 'Limb Skin Temp High',
    devices: [SENSOR_TYPES.LIMB],
  },
  FALL_AUDIO: {
    code: '258169',
    message: 'Fall Detected',
  },
  POSITION_AUDIO: {
    code: '258173',
    message: 'Body Position > 2 Hours',
  },
};

export const VITALS_ALERT_CODES: AlertMetadataMapping = {
  ...AUDIO_ALERT_CODES,
  HR_LOW_VISUAL: {
    code: '258054',
    message: 'HR Low',
  },
  HR_HIGH_VISUAL: {
    code: '258050',
    message: 'HR High',
  },
  RR_LOW_VISUAL: {
    code: '258058',
    message: 'RR Low',
  },
  RR_HIGH_VISUAL: {
    code: '258062',
    message: 'RR High',
  },
  SPO2_LOW_VISUAL: {
    code: '258066',
    message: 'SpO2 Low',
  },
  SPO2_HIGH_VISUAL: {
    code: '258070',
    message: 'SpO2 High',
  },
  PR_LOW_VISUAL: {
    code: '258178',
    message: 'PR Low',
  },
  PR_HIGH_VISUAL: {
    code: '258182',
    message: 'PR High',
  },
  SYS_LOW_VISUAL: {
    code: '258074',
    message: 'NIBP SYS Low',
  },
  SYS_HIGH_VISUAL: {
    code: '258078',
    message: 'NIBP SYS High',
  },
  DIA_LOW_VISUAL: {
    code: '258082',
    message: 'NIBP DIA Low',
  },
  DIA_HIGH_VISUAL: {
    code: '258086',
    message: 'NIBP DIA High',
  },
  BODY_TEMP_LOW_VISUAL: {
    code: '258162',
    message: 'Body Temp Low',
  },
  BODY_TEMP_HIGH_VISUAL: {
    code: '258166',
    message: 'Body Temp High',
  },
  CHEST_TEMP_LOW_VISUAL: {
    code: '258154',
    message: 'Chest Skin Temp Low',
    devices: [SENSOR_TYPES.ADAM, SENSOR_TYPES.CHEST],
  },
  CHEST_TEMP_HIGH_VISUAL: {
    code: '258158',
    message: 'Chest Skin Temp High',
    devices: [SENSOR_TYPES.ADAM, SENSOR_TYPES.CHEST],
  },
  LIMB_TEMP_LOW_VISUAL: {
    code: '258154',
    message: 'Limb Skin Temp Low',
    devices: [SENSOR_TYPES.LIMB],
  },
  LIMB_TEMP_HIGH_VISUAL: {
    code: '258158',
    message: 'Limb Skin Temp High',
    devices: [SENSOR_TYPES.LIMB],
  },
  FALL_VISUAL: {
    code: '258170',
    message: 'Fall Detected',
  },
  POSITION_VISUAL: {
    code: '258174',
    message: 'Body Position > 2 Hours',
  },
};

export const DEVICE_ALERT_CODES: AlertMetadataMapping = {
  OUT_OF_RANGE_ALERT: {
    code: '258098',
    message: 'Sensor out of range',
    waveformMessage: 'OUT OF RANGE, MOVE SENSOR CLOSER',
  },
  LOW_SIGNAL_ALERT: {
    code: '258118',
    message: 'Low signal',
  },
  CRITICAL_BATTERY_ALERT: {
    code: '258106',
    message: 'Critical sensor battery',
  },
  LOW_BATTERY_ALERT: {
    code: '258102',
    message: 'Low sensor battery',
  },
  PM_LOW_BATTERY_ALERT: {
    code: '258102',
    message: 'Monitor low battery',
    devices: [SENSOR_TYPES.PATIENT_MONITOR],
  },
  SENSOR_FAILURE_ALERT: {
    code: '258138',
    message: 'Sensor failure',
    waveformMessage: 'SENSOR FAILURE, REPLACE SENSOR',
  },
  LEAD_OFF_ALERT: {
    code: '258110',
    message: 'Lead-off',
    waveformMessage: 'ECG LEAD-OFF',
  },
  POOR_SKIN_CONTACT_ALERT: {
    code: '258146',
    message: 'Poor skin contact',
    waveformMessage: 'PPG POOR SKIN CONTACT',
  },
  LOOSE_SLEEVE_ALERT: {
    code: '258142',
    message: 'Loose sleeve',
  },
  WEAK_PULSE_ALERT: {
    code: '258150',
    message: 'Weak pulse',
  },
  MOVEMENT_DETECTED_ALERT: {
    code: '258134',
    message: 'Movement detected',
  },
  FINGER_NOT_DETECTED_ALERT: {
    code: '258122',
    message: 'Finger not detected',
    waveformMessage: 'PPG POOR SKIN CONTACT',
  },
  SENSOR_ERROR_ALERT: {
    code: '258126',
    message: 'Sensor error',
    waveformMessage: 'SENSOR ERROR, RECONNECT SENSOR PROBE',
  },
  SYSTEM_ERROR_ALERT: {
    code: '258130',
    message: 'System error',
    waveformMessage: 'SYSTEM ERROR, RESTART SENSOR',
  },
  MODULE_FAILURE_ALERT: {
    code: '258114',
    message: 'Sensor failure',
    waveformMessage: 'SENSOR FAILURE, REPLACE SENSOR',
  },
  MONITOR_NOT_AVAILABLE_ALERT: {
    code: 'MonitorNotAvailable', // Internal code used only in CMS for flaggin a Monitor not being Available,
    message: 'Monitor not available',
    waveformMessage: 'PATIENT MONITOR IS NOT AVAILABLE',
  },
};

export const SUPPORTED_ALERT_CODES = Object.values({
  ...VITALS_ALERT_CODES,
  ...DEVICE_ALERT_CODES,
}).map((alertMapping) => alertMapping.code);

export const METRIC_SENSOR_MAP: Record<string, SENSOR_TYPES[]> = {
  [METRIC_INTERNAL_CODES.ECG]: [SENSOR_TYPES.CHEST],
  [METRIC_INTERNAL_CODES.PLETH]: [SENSOR_TYPES.NONIN, SENSOR_TYPES.LIMB],
  [METRIC_INTERNAL_CODES.RR]: [SENSOR_TYPES.CHEST],
  [METRIC_INTERNAL_CODES.HR]: [SENSOR_TYPES.ADAM, SENSOR_TYPES.CHEST],
  [METRIC_INTERNAL_CODES.SPO2]: [SENSOR_TYPES.LIMB, SENSOR_TYPES.NONIN],
  [METRIC_INTERNAL_CODES.PR]: [SENSOR_TYPES.LIMB, SENSOR_TYPES.NONIN],
  [METRIC_INTERNAL_CODES.PI]: [SENSOR_TYPES.LIMB, SENSOR_TYPES.NONIN],
  [METRIC_INTERNAL_CODES.RR_METRIC]: [SENSOR_TYPES.CHEST, SENSOR_TYPES.ADAM],
  [METRIC_INTERNAL_CODES.PULSE]: [SENSOR_TYPES.BP],
  [METRIC_INTERNAL_CODES.NIBP]: [SENSOR_TYPES.BP],
  [METRIC_INTERNAL_CODES.BODY_TEMP]: [SENSOR_TYPES.THERMOMETER],
  [METRIC_INTERNAL_CODES.CHEST_TEMP]: [SENSOR_TYPES.ADAM, SENSOR_TYPES.CHEST],
  [METRIC_INTERNAL_CODES.LIMB_TEMP]: [SENSOR_TYPES.LIMB],
  [METRIC_INTERNAL_CODES.FALLS]: [SENSOR_TYPES.ADAM, SENSOR_TYPES.CHEST],
  [METRIC_INTERNAL_CODES.POSITION]: [SENSOR_TYPES.ADAM, SENSOR_TYPES.CHEST],
  [METRIC_INTERNAL_CODES.POSITION_DURATION]: [SENSOR_TYPES.ADAM, SENSOR_TYPES.CHEST],
  [METRIC_INTERNAL_CODES.MAP]: [SENSOR_TYPES.BP],
};

export const CONTINUOUS_METRICS = [
  METRIC_INTERNAL_CODES.HR,
  METRIC_INTERNAL_CODES.PLETH,
  METRIC_INTERNAL_CODES.PR,
  METRIC_INTERNAL_CODES.PI,
  METRIC_INTERNAL_CODES.RR_METRIC,
  METRIC_INTERNAL_CODES.BODY_TEMP,
  METRIC_INTERNAL_CODES.CHEST_TEMP,
  METRIC_INTERNAL_CODES.LIMB_TEMP,
  METRIC_INTERNAL_CODES.FALLS,
  METRIC_INTERNAL_CODES.POSITION,
  METRIC_INTERNAL_CODES.POSITION_DURATION,
  METRIC_INTERNAL_CODES.BODY_ANGLE,
];

export const METRIC_VITALS_ALERTS_MAP: Record<string, string[]> = {
  HR: [VITALS_ALERT_CODES.HR_LOW_VISUAL.code, VITALS_ALERT_CODES.HR_HIGH_VISUAL.code],
  SPO: [VITALS_ALERT_CODES.SPO2_LOW_VISUAL.code, VITALS_ALERT_CODES.SPO2_HIGH_VISUAL.code],
};

export type VitalMetricInternalCodes =
  | METRIC_INTERNAL_CODES.HR
  | METRIC_INTERNAL_CODES.SPO2
  | METRIC_INTERNAL_CODES.PR
  | METRIC_INTERNAL_CODES.RR_METRIC
  | METRIC_INTERNAL_CODES.NIBP
  | METRIC_INTERNAL_CODES.BODY_TEMP
  | METRIC_INTERNAL_CODES.CHEST_TEMP
  | METRIC_INTERNAL_CODES.LIMB_TEMP
  | METRIC_INTERNAL_CODES.FALLS
  | METRIC_INTERNAL_CODES.POSITION;
