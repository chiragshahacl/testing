import {
  AlarmRecord,
  Alert,
  AlertMetadata,
  AlertMetadataMapping,
  DeviceAlert,
  VitalsAlert,
} from '@/types/alerts';
import {
  ALERT_PRIORITY,
  ALERT_TYPES,
  AUDIO_ALERT_CODES,
  DEVICE_ALERT_CODES,
  DEVICE_CODES,
  VITALS_ALERT_CODES,
} from '@/utils/metricCodes';
import moment from 'moment';
import { v4 as uuidv4 } from 'uuid';
import { SENSOR_TYPES } from '../types/sensor';
import { BedType } from '@/types/bed';
import { PatientPrimaryID, PatientSessionAlert } from '@/types/patient';
import { momentDurationToHourMinutesSeconds } from './moment';

const LOW_PRIORITY_ALERT_COLOR = '#75F8FC';
const HIGH_PRIORITY_ALERT_COLOR = '#FF4C42';
const MEDIUM_PRIORITY_ALERT_COLOR = '#F6C905';
export const ALERT_TEXT_COLOR = '#000000';

/**
 * Transforms an Alert Priority into a numberic value, where a higher number
 * is higher priority
 */
export const getAlertPriorityValue = (priority: string) => {
  switch (priority) {
    case ALERT_PRIORITY.HIGH:
    case ALERT_PRIORITY.INTERNAL:
      return 3;
    case ALERT_PRIORITY.MEDIUM:
      return 2;
    default:
      return 1;
  }
};

/**
 * Returns metadata of a specific type of technical alert for a specific device
 */
export const getDeviceAlert = (code: string, deviceCode: SENSOR_TYPES) =>
  getAlert(code, deviceCode, DEVICE_ALERT_CODES);

/**
 * Returns metadata of a specific type of vitals alert for a specific device
 */
export const getVitalAlert = (code: string, deviceCode: SENSOR_TYPES) =>
  getAlert(code, deviceCode, VITALS_ALERT_CODES);

const getAlert = (
  code: string,
  deviceCode: SENSOR_TYPES,
  alertCodes: AlertMetadataMapping
): AlertMetadata | null => {
  const alerts = Object.values(alertCodes).filter((alert) => alert.code === code);
  if (alerts.length === 1) {
    return alerts[0];
  }

  const deviceAlerts = alerts.filter(
    (alert) => alert.devices && alert.devices.includes(deviceCode)
  );

  if (deviceAlerts.length === 1) {
    return deviceAlerts[0];
  }

  const noDeviceAlerts = alerts.filter((alert) => typeof alert.devices === 'undefined'); // if no device is specified, it uses the first one

  return noDeviceAlerts[0] || null;
};

/**
 * Returns a new Alert for Lost Connection error. This alert is different depending
 * if there is an internet connection (Data Error alert),
 * or if there is NOT (Network Error Alert)
 */
export const generateLostConnectionAlert = (networkIsOnline: boolean): Alert => {
  if (!networkIsOnline)
    return {
      type: ALERT_TYPES.DEVICE,
      id: 'network-error-alert',
      code: 'NETWORK_ERROR',
      deviceCode: 'CMS',
      priority: ALERT_PRIORITY.HIGH,
      acknowledged: false,
      timestamp: new Date().toISOString(),
    };
  return {
    type: ALERT_TYPES.DEVICE,
    id: 'data-error-alert',
    code: 'DATA_ERROR',
    deviceCode: 'CMS',
    priority: ALERT_PRIORITY.MEDIUM,
    acknowledged: false,
    timestamp: new Date().toISOString(),
  };
};

/**
 * Retrieves the message for the highest priority alert passed (if any)
 */
export const getHighestPriorityAlertTitle = (
  alerts: (DeviceAlert | VitalsAlert)[],
  type: ALERT_TYPES
) => {
  alerts.sort((a, b) => {
    if (a.priority === b.priority) {
      return moment(b.timestamp).diff(moment(a.timestamp));
    }
    return getAlertPriorityValue(b.priority) - getAlertPriorityValue(a.priority);
  });

  if (alerts.length === 0) {
    return '';
  }

  return type === ALERT_TYPES.VITALS
    ? getVitalAlert(alerts[0].code, alerts[0].deviceCode as SENSOR_TYPES)?.message
    : getDeviceAlert(alerts[0].code, alerts[0].deviceCode as SENSOR_TYPES)?.message;
};

/**
 * Returns priority value of the highest priority alert passed
 */
export const getHighestPriorityFromAlerts = (alerts: (DeviceAlert | VitalsAlert)[]) => {
  if (alerts.find((alert) => alert.priority === ALERT_PRIORITY.HIGH)) {
    return ALERT_PRIORITY.HIGH;
  }
  if (alerts.find((alert) => alert.priority === ALERT_PRIORITY.MEDIUM)) {
    return ALERT_PRIORITY.MEDIUM;
  }
  return ALERT_PRIORITY.LOW;
};

/**
 * Returns the color associated with the highest priority alert passed
 */
export const getHighestPriorityAlertColor = (alerts: (DeviceAlert | VitalsAlert)[]) => {
  if (alerts.find((alert) => alert.priority === ALERT_PRIORITY.HIGH)) {
    return HIGH_PRIORITY_ALERT_COLOR;
  }
  if (alerts.find((alert) => alert.priority === ALERT_PRIORITY.MEDIUM)) {
    return MEDIUM_PRIORITY_ALERT_COLOR;
  }
  return LOW_PRIORITY_ALERT_COLOR;
};

/**
 * Returns the waveform message of the highest priority alert passed (if any)
 */
export const getHighestPriorityWaveformAlert = (alerts: DeviceAlert[]): DeviceAlert | undefined => {
  const waveformAlerts: DeviceAlert[] = alerts.filter(({ waveformMessage }) => !!waveformMessage);

  if (waveformAlerts.length > 0) {
    return waveformAlerts.reduce((highestPriorityAlert, newAlert) =>
      getAlertPriorityValue(newAlert.priority) >
        getAlertPriorityValue(highestPriorityAlert.priority) ||
      (newAlert.priority === highestPriorityAlert.priority &&
        moment(newAlert.timestamp).isAfter(moment.now()))
        ? newAlert
        : highestPriorityAlert
    );
  }

  return undefined;
};

/**
 * Returns the color associated with a specific alert priority
 */
export const getAlertColor = (alertPriority?: ALERT_PRIORITY): string | undefined => {
  switch (alertPriority) {
    case ALERT_PRIORITY.HIGH:
      return HIGH_PRIORITY_ALERT_COLOR;
    case ALERT_PRIORITY.MEDIUM:
      return MEDIUM_PRIORITY_ALERT_COLOR;
    case ALERT_PRIORITY.INTERNAL:
      return undefined;
    default:
      return LOW_PRIORITY_ALERT_COLOR;
  }
};

/**
 * Determines if a specific alert code is either a Vitals Alert or a Technical Alert
 */
export const getAlertTypeByCode = (alertCode: string): ALERT_TYPES | null => {
  if (Object.values(VITALS_ALERT_CODES).findIndex(({ code }) => code === alertCode) >= 0) {
    return ALERT_TYPES.VITALS;
  }
  if (Object.values(DEVICE_ALERT_CODES).findIndex(({ code }) => code === alertCode) >= 0) {
    return ALERT_TYPES.DEVICE;
  }
  return null;
};

/**
 * Returns the CSS class associated with a specific alert priority
 */
export const getAlertClass = (priority?: ALERT_PRIORITY) => {
  if (!priority) return '';
  switch (priority) {
    case ALERT_PRIORITY.HIGH:
      return 'metricCardWithHighAlert';
    case ALERT_PRIORITY.MEDIUM:
      return 'metricCardWithMedAlert';
    case ALERT_PRIORITY.INTERNAL:
      return '';
    default:
      return 'metricCardWithLowAlert';
  }
};

/**
 * Checks if an alert with the same code and device is present in the alert list passed
 */
export const isAlertActive = (alertObject: Alert, alertList: Alert[] = []) =>
  alertList.some(
    (currentAlert) =>
      alertObject.code === currentAlert.code &&
      (!alertObject.deviceCode ||
        !currentAlert.deviceCode ||
        alertObject.deviceCode === currentAlert.deviceCode)
  );

/**
 * Removes and alert from a list with the same code and device (if applicable) as the
 * alert passed
 */
export const removeAlertFromListByCode = <T extends Alert | DeviceAlert | VitalsAlert>(
  alertObject: T,
  alertList: T[]
) =>
  alertList.filter(
    (alert) =>
      alert.code !== alertObject.code ||
      (alert.deviceCode && alertObject.deviceCode && alert.deviceCode !== alertObject.deviceCode)
  );

const deviceAlertsCodes: string[] = Object.values(DEVICE_ALERT_CODES).map((alert) => alert.code);
const audioAlertCodes: string[] = Object.values(AUDIO_ALERT_CODES).map((alert) => alert.code);

/**
 * Checks if an audio alert should be played based on an alerts list
 */
export const checkAudioAlertsExist = (alerts: Alert[]): boolean =>
  alerts.filter((alert) => [...deviceAlertsCodes, ...audioAlertCodes].includes(alert.code)).length >
  0;

/**
 * Checks if a list of alerts contains a Monitor Not Available alert
 */
export const isMonitorNotAvailableAlertPresent = (alerts: Alert[]) => {
  return (
    alerts.findIndex(
      (alert) => alert.code === DEVICE_ALERT_CODES.MONITOR_NOT_AVAILABLE_ALERT.code
    ) >= 0
  );
};

/**
 * Returns a new Monitor Not Available Alert
 */
export const generateNewMonitorNotAvailableAlert = (): DeviceAlert => ({
  type: ALERT_TYPES.DEVICE,
  id: uuidv4(),
  code: DEVICE_ALERT_CODES.MONITOR_NOT_AVAILABLE_ALERT.code,
  deviceCode: 'Patient Monitor',
  priority: ALERT_PRIORITY.HIGH,
  acknowledged: false,
  timestamp: new Date().toISOString(),
});

/**
 * Returns a list of alerts that only include the alerts that are associated with
 * patients in a specific bed group
 */
export const filterAlertsByPatientInGroup = (
  alertsByPatientId: Record<PatientPrimaryID, Alert[]>,
  bedsInGroup: BedType[],
  bedsWithPatients: BedType[]
): Alert[] => {
  const bedPatientHash: Record<string, PatientPrimaryID> = {};
  bedsWithPatients.forEach((bed) => {
    if (bed.patient?.patientPrimaryIdentifier)
      bedPatientHash[bed.id] = bed.patient.patientPrimaryIdentifier;
  });
  return bedsInGroup.flatMap((bed) => alertsByPatientId[bedPatientHash[bed.id]] || []);
};

/**
 * Returns a list of alerts that only include the alerts that are associated with
 * the beds in a particular bed group
 */
export const filterAlertsByBedInGroup = (
  alertsByBedId: Record<string, Alert[]>,
  bedsInGroup: BedType[]
): Alert[] => bedsInGroup.flatMap((bed) => alertsByBedId[bed.id] || []);

const sessionAlertMessageLimitUpperThresholdIndicator = 'UPPER_THRESHOLD_PLACEHOLDER_INDICATOR';
const sessionAlertMessageLimitLowerThresholdIndicator = 'LOWER_THRESHOLD_PLACEHOLDER_INDICATOR';

const SessionAlertMessageByCodeAndSensor: Record<string, Record<string, string>> = {
  /** TODO: Handle internal alerts. The ones we want are the following:
    Network (from Central)	- No network available.
    PM (from Central)	- Patient monitor is not available
    System (from Central) - Data storage has an error.
   */

  // Vitals
  '258050': {
    all: `HR > ${sessionAlertMessageLimitUpperThresholdIndicator}`,
  },
  '258054': {
    all: `HR < ${sessionAlertMessageLimitLowerThresholdIndicator}`,
  },
  '258062': {
    all: `RR > ${sessionAlertMessageLimitUpperThresholdIndicator}`,
  },
  '258058': {
    all: `RR < ${sessionAlertMessageLimitLowerThresholdIndicator}`,
  },
  '258070': {
    all: `SpO2 > ${sessionAlertMessageLimitUpperThresholdIndicator}`,
  },
  '258066': {
    all: `SpO2 < ${sessionAlertMessageLimitLowerThresholdIndicator}`,
  },
  '258182': {
    'Viatom BP monitor': `Pulse > ${sessionAlertMessageLimitUpperThresholdIndicator}`,
    'ANNE Limb': `PR > ${sessionAlertMessageLimitUpperThresholdIndicator}`,
    'Nonin 3150': `PR > ${sessionAlertMessageLimitUpperThresholdIndicator}`,
  },
  '258178': {
    'Viatom BP monitor': `Pulse < ${sessionAlertMessageLimitLowerThresholdIndicator}`,
    'ANNE Limb': `PR < ${sessionAlertMessageLimitLowerThresholdIndicator}`,
    'Nonin 3150': `PR < ${sessionAlertMessageLimitLowerThresholdIndicator}`,
  },
  '258078': {
    all: `NIBP SYS > ${sessionAlertMessageLimitUpperThresholdIndicator}`,
  },
  '258074': {
    all: `NIBP SYS < ${sessionAlertMessageLimitLowerThresholdIndicator}`,
  },
  '258086': {
    all: `NIBP DIA > ${sessionAlertMessageLimitUpperThresholdIndicator}`,
  },
  '258082': {
    all: `NIBP DIA < ${sessionAlertMessageLimitLowerThresholdIndicator}`,
  },
  '258166': {
    all: `Body Temp > ${sessionAlertMessageLimitUpperThresholdIndicator}`,
  },
  '258162': {
    all: `Body Temp < ${sessionAlertMessageLimitLowerThresholdIndicator}`,
  },
  '258158': {
    'ANNE Limb': `Limb Skin Temp > ${sessionAlertMessageLimitUpperThresholdIndicator}`,
    'ANNE Chest': `Chest Skin Temp > ${sessionAlertMessageLimitUpperThresholdIndicator}`,
    ADAM: `Chest Skin Temp > ${sessionAlertMessageLimitUpperThresholdIndicator}`,
  },
  '258154': {
    'ANNE Limb': `Limb Skin Temp < ${sessionAlertMessageLimitLowerThresholdIndicator}`,
    'ANNE Chest': `Chest Skin Temp < ${sessionAlertMessageLimitLowerThresholdIndicator}`,
    ADAM: `Chest Skin Temp < ${sessionAlertMessageLimitLowerThresholdIndicator}`,
  },
  '258170': { all: 'Fall Detected' },
  '258174': {
    all: `Position > ${sessionAlertMessageLimitUpperThresholdIndicator} Hours`,
  },
  // Technicals
  '258098': {
    'ANNE Chest': 'ANNE Chest sensor - out of range',
    'ANNE Limb': 'ANNE Limb sensor - out of range',
    'Nonin 3150': 'Nonin 3150 - Sensor out of range',
  },
  '258118': {
    'ANNE Chest': 'ANNE Chest sensor - low signal',
    'ANNE Limb': 'ANNE Limb sensor - low signal',
  },
  '258106': {
    'ANNE Chest': 'ANNE Chest sensor - critical battery (< 5%)',
    'ANNE Limb': 'ANNE Limb sensor - critical battery (< 5%)',
  },
  '258102': {
    'ANNE Chest': 'ANNE Chest sensor - low battery (< 20%)',
    'ANNE Limb': 'ANNE Limb sensor - low battery (< 20%)',
    'Patient Monitor': 'Low tablet battery (<20%)',
  },
  '258138': {
    'ANNE Chest': 'ANNE Chest sensor - failure',
    'ANNE Limb': 'ANNE Limb sensor - failure',
    'Viatom BP monitor': 'BP2A - Sensor Failure',
  },
  '258114': {
    'ANNE Chest': 'ANNE Chest sensor - failure',
    'ANNE Limb': 'ANNE Limb sensor - failure',
  },
  '258110': { all: 'ANNE Chest sensor - lead off' },
  '258146': { all: 'ANNE Limb sensor - poor skin contact' },
  '258142': { all: 'BP2A - Loose Sleve' },
  '258150': { all: 'BP2A - Weak Pulse' },
  '258134': { all: 'BP2A - Movement Detected' },
  '258122': {
    all: 'Nonin 3150 - Finger not detected',
  },
  '258126': { all: 'Nonin 3150 - Sensor error' },
  '258130': { all: 'Nonin 3150 - System error' },
};

const getSessionAlertMessageFromCode = (
  code: string,
  deviceCode: string,
  limits: { upperLimit?: number | null; lowerLimit?: number | null }
) => {
  let alertMessage;
  if (!deviceCode) alertMessage = SessionAlertMessageByCodeAndSensor[code]?.['all'];
  else
    alertMessage =
      SessionAlertMessageByCodeAndSensor[code]?.[deviceCode] ??
      SessionAlertMessageByCodeAndSensor[code]?.['all'];

  if (alertMessage) {
    alertMessage = alertMessage.replaceAll(
      sessionAlertMessageLimitUpperThresholdIndicator,
      limits.upperLimit?.toString() || '??'
    );
    alertMessage = alertMessage.replaceAll(
      sessionAlertMessageLimitLowerThresholdIndicator,
      limits.lowerLimit?.toString() || '??'
    );
  }

  return alertMessage;
};

/**
 * Returns a list of AlarmRecords based on the received patient session alerts of
 * one patient
 */
export const fromSessionAlertsToAlarmRecords = (patientSessionAlerts: PatientSessionAlert[]) => {
  const newRecords: AlarmRecord[] = [];

  patientSessionAlerts.forEach((sessionAlert: PatientSessionAlert) => {
    const message = getSessionAlertMessageFromCode(sessionAlert.code, sessionAlert.deviceCode, {
      upperLimit: sessionAlert.upperLimit,
      lowerLimit: sessionAlert.lowerLimit,
    });
    const type = getAlertTypeByCode(sessionAlert.code);
    if (message && type) {
      const duration = moment.duration(
        moment(sessionAlert.endTime).diff(moment(sessionAlert.startTime))
      );
      newRecords.push({
        type,
        date: sessionAlert.startTime,
        time: sessionAlert.startTime,
        priority: sessionAlert.priority,
        message,
        duration: momentDurationToHourMinutesSeconds(duration),
      });
    }
  });
  return newRecords;
};

export enum TECHNICAL_ALERT_TYPE {
  HR = 'HR',
  SPO = 'SPO',
  RR_METRIC = 'RR_METRIC',
  BODY_TEMP = 'BODY_TEMP',
  CHEST_TEMP = 'CHEST_TEMP',
  FALLS = 'FALLS',
  BODY_POSITION = 'BODY_POSITION',
  PI = 'PI',
  PR = 'PR',
  LIMB_TEMP = 'LIMB_TEMP',
  PULSE = 'PULSE',
  NIBP = 'NIBP',
}

export const TECHNICAL_ALERT_MAPPING: {
  deviceCode: string;
  alertCodes: string[];
  technicalAlertTypes: TECHNICAL_ALERT_TYPE[];
}[] = [
  {
    deviceCode: DEVICE_CODES.ANNE_CHEST.type,
    alertCodes: [
      DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code,
      DEVICE_ALERT_CODES.MODULE_FAILURE_ALERT.code,
      DEVICE_ALERT_CODES.LEAD_OFF_ALERT.code,
    ],
    technicalAlertTypes: [
      TECHNICAL_ALERT_TYPE.HR,
      TECHNICAL_ALERT_TYPE.RR_METRIC,
      TECHNICAL_ALERT_TYPE.CHEST_TEMP,
      TECHNICAL_ALERT_TYPE.FALLS,
      TECHNICAL_ALERT_TYPE.BODY_POSITION,
    ],
  },
  {
    deviceCode: DEVICE_CODES.ADAM.type,
    alertCodes: [
      DEVICE_ALERT_CODES.POOR_SKIN_CONTACT_ALERT.code,
      DEVICE_ALERT_CODES.MODULE_FAILURE_ALERT.code,
      DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code,
    ],
    technicalAlertTypes: [
      TECHNICAL_ALERT_TYPE.HR,
      TECHNICAL_ALERT_TYPE.RR_METRIC,
      TECHNICAL_ALERT_TYPE.CHEST_TEMP,
      TECHNICAL_ALERT_TYPE.FALLS,
      TECHNICAL_ALERT_TYPE.BODY_POSITION,
    ],
  },
  {
    deviceCode: DEVICE_CODES.NONIN_3150.type,
    alertCodes: [
      DEVICE_ALERT_CODES.FINGER_NOT_DETECTED_ALERT.code,
      DEVICE_ALERT_CODES.SENSOR_ERROR_ALERT.code,
      DEVICE_ALERT_CODES.SYSTEM_ERROR_ALERT.code,
      DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code,
    ],
    technicalAlertTypes: [
      TECHNICAL_ALERT_TYPE.SPO,
      TECHNICAL_ALERT_TYPE.PI,
      TECHNICAL_ALERT_TYPE.PR,
    ],
  },
  {
    deviceCode: DEVICE_CODES.ANNE_LIMB.type,
    alertCodes: [
      DEVICE_ALERT_CODES.POOR_SKIN_CONTACT_ALERT.code,
      DEVICE_ALERT_CODES.MODULE_FAILURE_ALERT.code,
      DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code,
    ],
    technicalAlertTypes: [
      TECHNICAL_ALERT_TYPE.SPO,
      TECHNICAL_ALERT_TYPE.PI,
      TECHNICAL_ALERT_TYPE.PR,
      TECHNICAL_ALERT_TYPE.LIMB_TEMP,
    ],
  },
  {
    deviceCode: DEVICE_CODES.VIATOM_BP.type,
    alertCodes: [
      DEVICE_ALERT_CODES.LOOSE_SLEEVE_ALERT.code,
      DEVICE_ALERT_CODES.MOVEMENT_DETECTED_ALERT.code,
      DEVICE_ALERT_CODES.WEAK_PULSE_ALERT.code,
      DEVICE_ALERT_CODES.SENSOR_FAILURE_ALERT.code,
    ],
    technicalAlertTypes: [TECHNICAL_ALERT_TYPE.PULSE, TECHNICAL_ALERT_TYPE.NIBP],
  },
];
