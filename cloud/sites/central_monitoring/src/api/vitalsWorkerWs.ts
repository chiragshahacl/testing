import { z } from 'zod';

import { PatientPrimaryID } from '@/types/patient';
import { WebsocketFiltersMessage } from '@/types/websocketFilters';
import { WaveformProcessor } from '@/utils/websocket/waveformProcessors/WaveformProcessor';
import { EcgWaveformProcessor } from '@/utils/websocket/waveformProcessors/ecgWaveformProcessor';
import { PlethWaveformProcessor } from '@/utils/websocket/waveformProcessors/plethWaveformProcessor';
import { EVENT_CODES, METRIC_CODES, WS_CODES } from '@/utils/metricCodes';
import { RESPONSE_STATUS } from '@/utils/status';
import { sendWebsocketMessage } from '@/utils/websocket/metricsFilters';
import { WORKER_FLOWS } from '@/utils/websocket/flows';
import { RawSocketMessage } from '@/types/socketMessage';
import { workerFlowEventSchema } from '@/schemas/workerFlowEvent';
import { clone, cloneDeep } from 'lodash';
import { BedsideAudioAlarmStatus } from '@/types/alerts';

let socket: WebSocket;

const DEFAULT_RECONNECT_TIME = 5000;
const MAX_RECONNECT_TIME = 30000;

const EMPTY_FILTERS: WebsocketFiltersMessage = {
  patientIdentifiers: [],
  filters: {},
};

const packetSizePerGraph: Record<string, number> = {
  [WS_CODES.ECG]: 10,
  [WS_CODES.PLETH]: 1,
  [WS_CODES.RR]: 1,
};

const DEVICE_EVENTS = [
  EVENT_CODES.DEVICE_CREATED_EVENT,
  EVENT_CODES.DEVICE_UPDATED_EVENT,
  EVENT_CODES.ASSIGN_DEVICE_LOCATION_EVENT,
  EVENT_CODES.UNASSIGN_DEVICE_LOCATION_EVENT,
];

const PATIENT_EVENTS = [
  EVENT_CODES.PATIENT_ENCOUNTER_STARTED,
  EVENT_CODES.PATIENT_ENCOUNTER_PLANNED,
  EVENT_CODES.PATIENT_ENCOUNTER_COMPLETED,
];

const BED_GROUP_EVENTS = [
  EVENT_CODES.BED_GROUP_DELETED_EVENT,
  EVENT_CODES.BED_GROUP_UPDATED_EVENT,
  EVENT_CODES.BED_GROUP_CREATED_EVENT,
  EVENT_CODES.BED_ASSIGNED_TO_GROUP_EVENT,
  EVENT_CODES.BED_REMOVED_FROM_GROUP_EVENT,
];

const BED_EVENTS = [
  EVENT_CODES.BED_CREATED_EVENT,
  EVENT_CODES.BED_DELETED_EVENT,
  EVENT_CODES.BED_UPDATED_EVENT,
];
const selectedPatientFilters = [
  ...Object.keys(METRIC_CODES),
  WS_CODES.DEVICE_BATTERY,
  WS_CODES.DEVICE_BATTERY_STATUS,
  WS_CODES.DEVICE_SIGNAL,
  WS_CODES.DEVICE_STATUS,
];

let manualDisconnect = false;
let currentDisconnectTime = 0;

// The second key is the graph code
let graphDataPerGraphPerPatient: Record<PatientPrimaryID, Record<string, (number | null)[]>> = {};
let dataRatePerGraphPerPatient: Record<PatientPrimaryID, Record<string, number>> = {};
let waveformProcessorPerGraphPerPatient: Record<
  PatientPrimaryID,
  Record<string, WaveformProcessor>
> = {};
let intervalsRunning: NodeJS.Timer[] = [];
let clearIntervalsRunning = false;
let filters: WebsocketFiltersMessage = clone(EMPTY_FILTERS);

const graphMessagePayloadSchema = z.object({
  // eslint-disable-next-line camelcase
  patient_primary_identifier: z.string(),
  code: z.string(),
  // eslint-disable-next-line camelcase
  sample_period: z.string(),
  samples: z.array(z.number()),
  // eslint-disable-next-line camelcase
  determination_period: z.string(),
});

const clearData = () => {
  if (!clearIntervalsRunning) {
    clearIntervalsRunning = true;
    graphDataPerGraphPerPatient = {};
    dataRatePerGraphPerPatient = {};
    waveformProcessorPerGraphPerPatient = {};
    intervalsRunning.forEach((interval) => {
      clearInterval(interval);
    });
    intervalsRunning = [];
    clearIntervalsRunning = false;
  }
};

// Accelerates graphs by sending more data per packet if data is starting to pile up in the buffers
const calcAmountOfPoints = (graphData: (number | null)[], rate: number, graphCode: string) => {
  const acceleratedAmountOfPoints = Math.ceil(
    (graphData.length * packetSizePerGraph[graphCode]) / rate
  );
  return Math.max(acceleratedAmountOfPoints, packetSizePerGraph[graphCode]);
};

const sendPackets = (patientId: string, code: string) => {
  if (
    graphDataPerGraphPerPatient &&
    graphDataPerGraphPerPatient[patientId] &&
    graphDataPerGraphPerPatient[patientId][code] &&
    dataRatePerGraphPerPatient &&
    dataRatePerGraphPerPatient[patientId] &&
    dataRatePerGraphPerPatient[patientId][code]
  ) {
    if (graphDataPerGraphPerPatient[patientId][code].length > 0) {
      const amountOfPoints = calcAmountOfPoints(
        graphDataPerGraphPerPatient[patientId][code],
        dataRatePerGraphPerPatient[patientId][code],
        code
      );
      postMessage({
        samples: graphDataPerGraphPerPatient[patientId][code].splice(0, amountOfPoints),
        pid: patientId,
        code,
        status: RESPONSE_STATUS.WAVEFORM,
      });
    }
  }
};

onmessage = (event: MessageEvent) => {
  const eventData = workerFlowEventSchema.safeParse(event.data);
  if (eventData.success) {
    switch (eventData.data.flow) {
      case WORKER_FLOWS.CONNECT:
        if (
          !socket ||
          socket.readyState === socket.CLOSED ||
          socket.readyState === socket.CLOSING
        ) {
          clearData();

          filters = clone(EMPTY_FILTERS);

          filters.patientIdentifiers = eventData.data.allPatients;

          if (eventData.data.allPatientFilters && eventData.data.allPatientFilters.length > 0) {
            // Set all patients filters if available
            filters.filters.codes = eventData.data.allPatientFilters;
          }
          if (eventData.data.selectedPatientId) {
            // Set selected patient filters if available
            filters.filters.patientFilters = {
              identifier: eventData.data.selectedPatientId,
              codes: selectedPatientFilters,
            };
          }
          const ignoreEcgFilter = eventData.data.ignoreEcgFilter;

          const socketUrl = eventData.data.socketUrl + `?token=${eventData.data.token}`;
          socket = new WebSocket(socketUrl);

          socket.onmessage = (message) => {
            if (currentDisconnectTime > 0) currentDisconnectTime = 0;
            const messageWithMetadata: RawSocketMessage = JSON.parse(
              message.data as string
            ) as RawSocketMessage;
            const payload = messageWithMetadata.payload;
            const eventType = messageWithMetadata.event_type;
            const pid = payload?.patient_primary_identifier;
            const code = payload?.code || '';

            if (PATIENT_EVENTS.includes(eventType)) {
              const eventState = messageWithMetadata.event_state;
              if (eventState) {
                postMessage({
                  status: RESPONSE_STATUS.PATIENT_REFRESH,
                  bedId: eventState.device?.location_id,
                  patientId: eventState.patient?.id,
                });
              }
            } else if (DEVICE_EVENTS.includes(eventType)) {
              const eventData = messageWithMetadata.event_state;
              if (eventData) {
                postMessage({
                  status: RESPONSE_STATUS.DEVICE_REFRESH,
                  deviceId: eventData.primary_identifier,
                  isPatientMonitor: !eventData.gateway_id,
                });
              }
            } else if (eventType === EVENT_CODES.DEVICE_DELETED_EVENT) {
              const eventData = messageWithMetadata.event_state;
              const previousState = messageWithMetadata.previous_state;
              if (eventData && previousState) {
                postMessage({
                  status: RESPONSE_STATUS.SENSOR_DISCONNECTED,
                  deviceId: eventData.primary_identifier,
                  patientPrimaryIdentifier: messageWithMetadata.entity_id,
                  deviceType: previousState.model_number,
                });
              }
            } else if (BED_GROUP_EVENTS.includes(eventType)) {
              postMessage({
                status: RESPONSE_STATUS.BED_GROUP_REFRESH,
              });
            } else if (BED_EVENTS.includes(eventType)) {
              postMessage({ status: RESPONSE_STATUS.BEDS_REFRESH });
            } else if (eventType === EVENT_CODES.PATIENT_ENCOUNTER_CANCELLED) {
              const eventData = messageWithMetadata.event_state;
              if (eventData) {
                postMessage({
                  status: RESPONSE_STATUS.PATIENT_ENCOUNTER_CANCELLED,
                  bedId: eventData.device?.location_id,
                });
              }
            } else if (eventType === EVENT_CODES.VITAL_RANGE_CREATED_EVENT) {
              const eventData = messageWithMetadata.event_state;
              if (eventData) {
                postMessage({
                  status: RESPONSE_STATUS.NEW_RANGE,
                  deviceId: eventData.device_id,
                  code: eventData.code,
                  upperLimit: eventData.upper_limit,
                  lowerLimit: eventData.lower_limit,
                });
              }
            } else if (eventType === EVENT_CODES.PM_CONNECTION_STATUS_REPORT) {
              const newConnectionStatus = payload?.connection_status;
              postMessage({
                status: RESPONSE_STATUS.PM_STATUS_REPORT,
                newConnectionStatus,
                monitorId: payload?.device_primary_identifier,
              });
            } else if (eventType === EVENT_CODES.PM_CONFIGURATION_UPDATED) {
              if (payload) {
                postMessage({
                  status: RESPONSE_STATUS.BEDSIDE_AUDIO_ALERT_STATUS,
                  patientMonitorId: payload.device_primary_identifier,
                  newAudioAlarmStatus: !payload.audio_enabled
                    ? BedsideAudioAlarmStatus.OFF
                    : payload.audio_pause_enabled
                    ? BedsideAudioAlarmStatus.PAUSED
                    : BedsideAudioAlarmStatus.ACTIVE,
                });
              }
            } else if (eventType === EVENT_CODES.PATIENT_SESSION_CLOSED_EVENT) {
              if (pid) {
                postMessage({
                  status: RESPONSE_STATUS.PATIENT_SESSION_CLOSED,
                  pid,
                });
              }
            } else if (eventType === EVENT_CODES.ALERT_DEACTIVATED_EVENT) {
              const eventState = messageWithMetadata.event_state;
              if (eventState && eventState.code) {
                postMessage({
                  status: RESPONSE_STATUS.REFRESH_ALERT_HISTORY,
                  patientId: eventState.patient_id,
                });
              }
            } else if (
              eventType === EVENT_CODES.OBSERVATION_CREATED_EVENT ||
              eventType === EVENT_CODES.OBSERVATION_DELETED_EVENT ||
              eventType === EVENT_CODES.DEVICE_ALERT_CREATED ||
              eventType === EVENT_CODES.DEVICE_ALERT_DELETED ||
              eventType === EVENT_CODES.MULTIPLE_DEVICE_ALERTS_UPDATED ||
              eventType === EVENT_CODES.MULTIPLE_OBSERVATIONS_UPDATED
            ) {
              const eventState = messageWithMetadata.event_state;
              postMessage({
                status: RESPONSE_STATUS.ALERT,
                code: eventState?.code,
              });
            } else if (code === WS_CODES.ECG || code === WS_CODES.PLETH || code === WS_CODES.RR) {
              const graphMessageData = graphMessagePayloadSchema.safeParse(payload);
              if (graphMessageData.success) {
                const graphPid = graphMessageData.data.patient_primary_identifier;
                const newData: (number | null)[] = [];
                const samplePeriod = Number(
                  graphMessageData.data.sample_period.slice(0, -1).substring(2)
                );
                const determinationPeriod = Number(
                  graphMessageData.data.determination_period.slice(0, -1).substring(2)
                );

                if (!waveformProcessorPerGraphPerPatient[graphPid]) {
                  waveformProcessorPerGraphPerPatient[graphPid] = {};
                }
                if (!waveformProcessorPerGraphPerPatient[graphPid][code]) {
                  if (code === WS_CODES.ECG) {
                    waveformProcessorPerGraphPerPatient[graphPid][code] = new EcgWaveformProcessor(
                      1 / samplePeriod
                    );
                  }
                  if (code === WS_CODES.PLETH) {
                    waveformProcessorPerGraphPerPatient[graphPid][code] =
                      new PlethWaveformProcessor();
                  }
                }

                graphMessageData.data.samples.forEach((sample: number) => {
                  if (code === WS_CODES.ECG && ignoreEcgFilter) {
                    newData.push(sample);
                  } else if (code === WS_CODES.ECG || code === WS_CODES.PLETH) {
                    const newValue =
                      waveformProcessorPerGraphPerPatient[graphPid][code].feedDatum(sample);
                    newData.push(newValue);
                  } else {
                    newData.push(sample);
                  }
                });

                if (!graphDataPerGraphPerPatient[graphPid]) {
                  // Generate data object for new patient
                  graphDataPerGraphPerPatient[graphPid] = {};
                }
                if (!dataRatePerGraphPerPatient[graphPid]) {
                  dataRatePerGraphPerPatient[graphPid] = {};
                }
                dataRatePerGraphPerPatient[graphPid][code] = determinationPeriod / samplePeriod;
                if (!graphDataPerGraphPerPatient[graphPid][code]) {
                  graphDataPerGraphPerPatient[graphPid][code] = [...newData];
                  sendPackets(graphPid, code);
                  const newInterval = setInterval(() => {
                    sendPackets(graphPid, code);
                  }, packetSizePerGraph[code] * 1000 * samplePeriod);
                  intervalsRunning.push(newInterval);
                } else {
                  graphDataPerGraphPerPatient[graphPid][code] =
                    graphDataPerGraphPerPatient[graphPid][code].concat(newData);
                }
              }
            } else if (
              [
                WS_CODES.DEVICE_BATTERY,
                WS_CODES.DEVICE_BATTERY_STATUS,
                WS_CODES.DEVICE_SIGNAL,
                WS_CODES.DEVICE_STATUS,
              ].includes(code)
            ) {
              if (payload?.samples) {
                postMessage({
                  samples: payload.samples[0],
                  sensorId: payload?.device_primary_identifier,
                  pid,
                  code,
                  unitCode: payload?.unit_code,
                  status:
                    code === WS_CODES.DEVICE_BATTERY_STATUS
                      ? RESPONSE_STATUS.BATTERY_STATUS
                      : RESPONSE_STATUS.SENSOR_DATA,
                });
              }
            } else if (payload && payload.samples && payload.samples.length > 0) {
              postMessage({
                samples: payload.samples[0],
                pid,
                code,
                unitCode: payload.unit_code,
                deviceCode: payload.device_code,
                status: RESPONSE_STATUS.METRIC,
                timestamp: payload.determination_time,
              });
            }
          };

          socket.onclose = () => {
            clearData();
            if (!manualDisconnect) {
              setTimeout(() => {
                postMessage({
                  status: RESPONSE_STATUS.RECONNECTION_NEEDED,
                });
              }, currentDisconnectTime);
              currentDisconnectTime = Math.min(
                MAX_RECONNECT_TIME,
                currentDisconnectTime + DEFAULT_RECONNECT_TIME
              );
            } else {
              manualDisconnect = false;
            }
          };

          const filtersCopy = cloneDeep(filters);
          filtersCopy.sendCache = true;
          void sendWebsocketMessage(socket, JSON.stringify(filtersCopy));
        }
        break;
      case WORKER_FLOWS.DISCONNECT:
        clearData();
        if (socket && socket.readyState === socket.OPEN) {
          manualDisconnect = true;
          socket.close();
        }
        break;
      case WORKER_FLOWS.TEST_DISCONNECTION:
        if (socket && socket.readyState === socket.OPEN) {
          socket.close();
        }
        break;
      case WORKER_FLOWS.UPDATE_SELECTED_PATIENT:
        if (
          socket &&
          (socket.readyState === socket.OPEN || socket.readyState === socket.CONNECTING) //
        ) {
          if (eventData.data.patientPrimaryIdentifier) {
            filters.filters.patientFilters = {
              identifier: eventData.data.patientPrimaryIdentifier,
              codes: selectedPatientFilters,
            };
          } else {
            filters.filters.patientFilters = undefined;
          }

          void sendWebsocketMessage(socket, JSON.stringify(filters));
        }
        break;
      case WORKER_FLOWS.UPDATE_SELECTED_GROUP:
        filters.patientIdentifiers = eventData.data.patientsPrimaryIdentifiers;
        if (
          socket &&
          (socket.readyState === socket.OPEN || socket.readyState === socket.CONNECTING)
        ) {
          const filtersCopy = cloneDeep(filters);
          filtersCopy.sendCache = true;
          void sendWebsocketMessage(socket, JSON.stringify(filtersCopy));
        }
        break;
    }
  }
};
