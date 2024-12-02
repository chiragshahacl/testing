import { BedsideAudioAlarmStatus } from '@/types/alerts';
import { SENSOR_TYPES } from '@/types/sensor';
import { RESPONSE_STATUS } from '@/utils/status';
import { z } from 'zod';

const bedGroupRefreshEventSchema = z.object({
  status: z.literal(RESPONSE_STATUS.BED_GROUP_REFRESH),
});

const bedsRefreshEventSchema = z.object({
  status: z.literal(RESPONSE_STATUS.BEDS_REFRESH),
});

const patientRefreshEventSchema = z.object({
  status: z.literal(RESPONSE_STATUS.PATIENT_REFRESH),
  bedId: z.string().nullable().optional(),
  patientId: z.string().nullable().optional(),
});

const pmStatusReportEventSchema = z.object({
  status: z.literal(RESPONSE_STATUS.PM_STATUS_REPORT),
  monitorId: z.string(),
  newConnectionStatus: z.boolean(),
});

const newRangeEventSchema = z.object({
  status: z.literal(RESPONSE_STATUS.NEW_RANGE),
  deviceId: z.string(),
  code: z.string(),
  upperLimit: z.string().or(z.number()).optional().nullable(),
  lowerLimit: z.string().or(z.number()).optional().nullable(),
});

const deviceRefreshEventSchema = z.object({
  status: z.literal(RESPONSE_STATUS.DEVICE_REFRESH),
  deviceId: z.string(),
  isPatientMonitor: z.boolean(),
});

const sensorDisconnectedEventSchema = z.object({
  status: z.literal(RESPONSE_STATUS.SENSOR_DISCONNECTED),
  deviceId: z.string(),
  patientPrimaryIdentifier: z.string(),
  deviceType: z.nativeEnum(SENSOR_TYPES),
});

const alertEventSchema = z.object({
  status: z.literal(RESPONSE_STATUS.ALERT),
  code: z.string().optional(),
});

const reconnectionNeededEventSchema = z.object({
  status: z.literal(RESPONSE_STATUS.RECONNECTION_NEEDED),
});

const newMetricEventSchema = z.object({
  status: z.literal(RESPONSE_STATUS.METRIC),
  code: z.string(),
  pid: z.string(),
  samples: z.number().or(z.string()).nullable(),
  unitCode: z.string().optional(),
  deviceCode: z.string().optional(),
  timestamp: z.string().or(z.number()).optional(),
  sensorId: z.string().optional(),
});

const newWaveformEventSchema = z.object({
  status: z.literal(RESPONSE_STATUS.WAVEFORM),
  code: z.string(),
  pid: z.string(),
  samples: z.array(z.number().or(z.null())),
});

const newSensorDataEventSchema = z.object({
  status: z.literal(RESPONSE_STATUS.SENSOR_DATA),
  code: z.string(),
  pid: z.string(),
  samples: z.number().or(z.string()).nullable(),
  unitCode: z.string().optional(),
  sensorId: z.string().optional(),
});

const newBatteryStatusEventSchema = z.object({
  status: z.literal(RESPONSE_STATUS.BATTERY_STATUS),
  code: z.string(),
  pid: z.string(),
  samples: z.string(),
  unitCode: z.string().optional(),
  sensorId: z.string().optional(),
});

const newBedsideAlertStatusEventSchema = z.object({
  status: z.literal(RESPONSE_STATUS.BEDSIDE_AUDIO_ALERT_STATUS),
  patientMonitorId: z.string(),
  newAudioAlarmStatus: z.nativeEnum(BedsideAudioAlarmStatus),
});

const patientSessionClosedEventSchema = z.object({
  status: z.literal(RESPONSE_STATUS.PATIENT_SESSION_CLOSED),
  pid: z.string(),
});

const patientEncounterCancelledEventSchema = z.object({
  status: z.literal(RESPONSE_STATUS.PATIENT_ENCOUNTER_CANCELLED),
  bedId: z.string(),
});

const refreshAlertHistoryEventSchema = z.object({
  status: z.literal(RESPONSE_STATUS.REFRESH_ALERT_HISTORY),
  patientId: z.string(),
});

export const workerMessageEventSchema = z.discriminatedUnion('status', [
  newRangeEventSchema,
  deviceRefreshEventSchema,
  sensorDisconnectedEventSchema,
  alertEventSchema,
  reconnectionNeededEventSchema,
  newMetricEventSchema,
  newWaveformEventSchema,
  newSensorDataEventSchema,
  bedGroupRefreshEventSchema,
  bedsRefreshEventSchema,
  patientRefreshEventSchema,
  pmStatusReportEventSchema,
  newBedsideAlertStatusEventSchema,
  patientSessionClosedEventSchema,
  patientEncounterCancelledEventSchema,
  refreshAlertHistoryEventSchema,
  newBatteryStatusEventSchema,
]);
