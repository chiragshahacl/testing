export const deviceAlertsPrimaryColor = '#75F8FC';
export const deviceAlertsSecondaryColor = '#1D252E';
export const vitalsAlertsPrimaryColor = '#E95454';
export const vitalsAlertsSecondaryColor = 'white';
export const disabledColor = 'rgba(193, 206, 226, 0.35)';
export const HR_TEXT_COLOR = 'vitals.green';
export const SPO_TEXT_COLOR = 'vitals.blue';
export const RR_TEXT_COLOR = 'vitals.lightGreen';

export const FULL_REFRESH_WAIT_TIME = 2000;
export const DEVICE_REFRESH_WAIT_TIME = 2000;
export const BED_GROUP_REFRESH_WAIT_TIME = 2000;
export const NEW_RANGES_WAIT_TIME = 2000;
export const REFETCH_ALERTS_WAIT_TIME = 200;
export const REFRESH_ALERT_HISTORY_WAIT_TIME = 500;
export const NO_CHEST_SENSOR_MESSAGE = 'NO ANNE CHEST SENSOR PAIRED';
export const NO_OXIMETER_MESSAGE = 'NO OXIMETER PAIRED';
export const NO_ASSIGNED_VALUE = 'N/A';
export const ERROR_VALUE = '-?-';
// Determines how long we wait for a patient monitor to send data before we consider it inactive (miliseconds)
export const MONITOR_NOT_AVAILABLE_THRESHOLD = 10000;
export const MONITOR_AVAILABILITY_CHECK_INTERVAL = 5000;

export const AUDIO_DISABLED_TIMER = 120;

export enum DISPLAY_ERRORS {
  NOT_AVAILABLE = 'NOT AVAILABLE',
  NO_ACTIVE_PATIENT_SESSION = 'NO ACTIVE PATIENT SESSION',
}

export const groupManagementErrors = {
  emptyGroup: 'Please first add beds to this group.',
  duplicateGroup: 'Bed group name already exists. Change or enter a new one.',
  failedToFetch: 'Failed to display bed groups. Please try again in a few minutes.',
  deleteFailed: 'Delete Group Error',
  modifyFailed: 'Modify Group Error',
};

export const bedManagementErrors = {
  bedNoAlreadyExists: 'Bed ID already exists. Change or enter a new one.',
  bedNoEmpty: 'Please enter the bed ID.',
  failedToFetch: 'Failed to display beds. Please try again in a few minutes.',
  failedToFetchPMs: 'Failed to display patient monitors. Please try again in a few minutes.',
  deleteFailed: 'Delete Bed Error',
  modifyFailed: 'Modify Bed Error',
  assignBedsFailed: 'Failed to assign beds',
};

export const requestErrors = {
  incorrectPassword: 'Incorrect password. Please try again.',
  serverError: 'Server error. Please try again in a few minutes.',
  tooManyAttempts: 'Too many attempts. Please try again in 15 minutes.',
  accountLocked: 'Account locked.',
};

export const measurementErrors = {
  measureFailed: 'Measure Failed',
};

export enum ALERT_AUDIO {
  ON = 'audio_on',
  OFF = 'audio_off',
}

export const UNSAVED_DATA_TYPE = {
  SETTING: 'setting',
  INFO: 'info',
};

export enum DISPLAY_DIRECTION {
  LTR = 'ltr',
  RTL = 'rtl',
}

export enum USER_TYPE {
  TECH = 'technical',
  NON_TECH = 'non-technical',
}

export const INTERVAL_VALIDATION_ERROR = 'Numbers only (1 - 100).';
export const PORT_VALIDATION_ERROR = 'Numbers only.';

export const ACTIVE_SESSION_KEY = 'sessionActive';
