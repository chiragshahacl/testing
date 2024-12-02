import { useAllSensors } from '@/api/useAllSensors';
import { useBeds } from '@/api/useBeds';
import { useGroups } from '@/api/useGroups';
import { usePatientMonitors } from '@/api/usePatientMonitors';
import {
  BED_GROUP_REFRESH_WAIT_TIME,
  DEVICE_REFRESH_WAIT_TIME,
  FULL_REFRESH_WAIT_TIME,
  NEW_RANGES_WAIT_TIME,
  REFETCH_ALERTS_WAIT_TIME,
  REFRESH_ALERT_HISTORY_WAIT_TIME,
} from '@/constants';
import { SocketWorkerMessage } from '@/types/socketMessage';
import { ALERT_TYPES, UNIT_CODES, getMetricCode } from '@/utils/metricCodes';
import { getCachedRuntimeConfig } from '@/utils/runtime';
import { RESPONSE_STATUS } from '@/utils/status';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import useDebounce from './useDebounce';
import useMetrics from './useMetricsData';
import usePatientData from './usePatientsData';
import useSession from './useSession';
import { get } from 'lodash';
import { WORKER_FLOWS } from '@/utils/websocket/flows';
import { workerMessageEventSchema } from '@/schemas/workerMessage';
import { findAssociatedBedPatient } from '@/utils/patientUtils';
import { isTokenValid } from '@/utils/jwtToken';
import { refreshTokenRequest } from '@/api/authApi';
import { STORAGE_KEYS } from '@/utils/storage';
import { redirectToLogin } from '@/utils/httpClient';
import { getAlertTypeByCode } from '@/utils/alertUtils';
import { useBedGroupVitalsAlerts } from '@/api/useGroupPatientAlerts';
import { usePatientSessionAlerts } from '@/api/usePatientSessionAlerts';

/**
 * @description Handles communication from the core CMS code to the WebWorker that communicates
 * with the realtime gateway websocket for current group realtime information
 * @returns Status of current worker and methods updating the connection and worker itself
 * workerReady - true if there is currently a created WebWorker for WS communication
 * startWorker - creates a new WebWorker if no worker exists
 * terminateWorker - terminates de current WebWorker and removes the reference
 * socketInitializer - starts a new WS connection with the current worker
 * socketCloseConnection - ends current WS connection through the WebWorker
 */
const useMessageSocketHandler = (allPatientsFilters: string[]) => {
  const { accessToken, refreshToken, setAccessToken } = useSession();
  const { activeGroupId, selectedBed, updateKeepAlive, getActiveGroup } = usePatientData();
  const {
    postNewMetric,
    postNewSensorMetric,
    postNewBedsideStatus,
    resetContinuousMetricsForDeviceForPatient,
  } = useMetrics();
  const patientMonitors = usePatientMonitors();
  const bedGroups = useGroups();
  const beds = useBeds();
  const allSensors = useAllSensors(activeGroupId);
  const bedGroupVitalsAlerts = useBedGroupVitalsAlerts(activeGroupId);
  const currentPatientAlertHistory = usePatientSessionAlerts(selectedBed?.patient?.patientId || '');

  const workerRef = useRef<Worker>();
  const groupPatientsIdentifiersRef = useRef<string[]>();
  const [workerReady, setWorkerReady] = useState(false);

  const selectedPatientId = useMemo(() => {
    return get(selectedBed, 'patient.patientPrimaryIdentifier', undefined);
  }, [selectedBed]);

  // TODO: Remove ignoreEcgFilter param when ECG Scale Indicator has been tested
  const socketValidator = useCallback(
    (ignoreEcgFilter?: boolean) => {
      const WSS_URL = getCachedRuntimeConfig().WSS_URL;
      if (WSS_URL) {
        const socketUrl = WSS_URL + '/realtime/vitals';
        workerRef.current?.postMessage({
          flow: WORKER_FLOWS.CONNECT,
          token: accessToken,
          socketUrl: socketUrl,
          allPatients: groupPatientsIdentifiersRef.current || [],
          allPatientFilters: allPatientsFilters,
          selectedPatientId: selectedPatientId || undefined,
          ignoreEcgFilter,
        });
      }
    },
    [accessToken, allPatientsFilters, selectedPatientId]
  );

  // TODO: Remove ignoreEcgFilter param when ECG Scale Indicator has been tested
  const socketInitializer = useCallback(
    (ignoreEcgFilter?: boolean) => {
      socketValidator(ignoreEcgFilter);
    },
    [socketValidator]
  );

  const socketCloseConnection = () => {
    workerRef.current?.postMessage({ flow: WORKER_FLOWS.DISCONNECT });
  };

  const refetchMonitors = useDebounce(() => {
    void patientMonitors.refetch();
  }, DEVICE_REFRESH_WAIT_TIME);

  const refetchSensors = useDebounce(() => {
    void allSensors.refetch();
  }, DEVICE_REFRESH_WAIT_TIME);

  const quickRefetchSensors = useDebounce(() => {
    void allSensors.refetch();
  }, 200);

  const refetchBeds = useDebounce(() => {
    void beds.refetch();
  }, FULL_REFRESH_WAIT_TIME);

  const refetchBedGroups = useDebounce(() => {
    void bedGroups.refetch();
  }, BED_GROUP_REFRESH_WAIT_TIME);

  const refetchGroupAlerts = useDebounce(() => {
    void bedGroupVitalsAlerts.refetch();
  }, REFETCH_ALERTS_WAIT_TIME);

  const refetchAlertHistory = useDebounce(() => {
    void currentPatientAlertHistory.refetch();
  }, REFRESH_ALERT_HISTORY_WAIT_TIME);

  const onNewRange = useDebounce(() => {
    void patientMonitors.refetch();
  }, NEW_RANGES_WAIT_TIME);

  const refreshTokenAndRestart = useCallback(async () => {
    if (refreshToken) {
      if (!accessToken || !isTokenValid(accessToken)) {
        const response = await refreshTokenRequest({ refresh: refreshToken });
        setAccessToken(response.data.access);
        localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, response.data.access);
      }
    }
  }, [refreshToken, setAccessToken, socketInitializer]);

  /**
   * Starts a new worker if no worker currently exists
   * @param onResetPatientAlerts Callback for handling resetting alerts of a patient
   * @param onWaveformData Callback for handling new waveform vital info received through the WS
   * getting data for all patients inside the current group
   */
  const startWorker = useCallback(
    (
      onResetPatientAlerts: (pid: string) => void,
      onWaveformData: (code: string, pid: string, rawData: SocketWorkerMessage) => void
    ) => {
      if (!workerRef.current) {
        workerRef.current = new Worker(new URL('../api/vitalsWorkerWs.ts', import.meta.url));
        if (workerRef.current) {
          workerRef.current.onmessage = (event: MessageEvent) => {
            const parseResult = workerMessageEventSchema.safeParse(event.data);
            if (parseResult.success) {
              const rawData = parseResult.data;
              const status = rawData.status;
              if (status === RESPONSE_STATUS.DEVICE_REFRESH) {
                const isPatientMonitor = rawData.isPatientMonitor;
                if (isPatientMonitor) {
                  refetchBeds();
                  refetchMonitors();
                  refetchSensors();
                } else {
                  refetchSensors();
                }
              }
              if (status === RESPONSE_STATUS.SENSOR_DISCONNECTED) {
                resetContinuousMetricsForDeviceForPatient(
                  rawData.deviceType,
                  rawData.patientPrimaryIdentifier
                );
                refetchSensors();
              }
              if (
                status === RESPONSE_STATUS.PATIENT_REFRESH ||
                status === RESPONSE_STATUS.BEDS_REFRESH ||
                status === RESPONSE_STATUS.PATIENT_ENCOUNTER_CANCELLED
              ) {
                refetchBeds();
              }
              if (status === RESPONSE_STATUS.BED_GROUP_REFRESH) {
                refetchBedGroups();
              } else if (status === RESPONSE_STATUS.REFRESH_ALERT_HISTORY) {
                refetchAlertHistory();
              } else if (status === RESPONSE_STATUS.NEW_RANGE) {
                onNewRange();
              } else if (status === RESPONSE_STATUS.PM_STATUS_REPORT) {
                const monitorId = rawData.monitorId;
                if (monitorId && rawData.newConnectionStatus) updateKeepAlive(monitorId);
              } else if (status === RESPONSE_STATUS.RECONNECTION_NEEDED) {
                const refreshTokenIsValid = refreshToken && isTokenValid(refreshToken);
                if (refreshTokenIsValid) {
                  void refreshTokenAndRestart();
                } else {
                  redirectToLogin();
                }
              } else if (status === RESPONSE_STATUS.ALERT) {
                const code = rawData.code;
                const type = code ? getAlertTypeByCode(code) : null;
                if (type === ALERT_TYPES.DEVICE) {
                  quickRefetchSensors();
                } else if (type === ALERT_TYPES.VITALS) {
                  refetchGroupAlerts();
                } else {
                  // Multiple alerts updated, as it does not have a single code
                  quickRefetchSensors();
                  refetchGroupAlerts();
                }
              } else if (status === RESPONSE_STATUS.WAVEFORM) {
                onWaveformData(rawData.code, rawData.pid, rawData);
              } else if (status === RESPONSE_STATUS.BEDSIDE_AUDIO_ALERT_STATUS) {
                postNewBedsideStatus(rawData.patientMonitorId, rawData.newAudioAlarmStatus);
              } else if (status === RESPONSE_STATUS.PATIENT_SESSION_CLOSED) {
                onResetPatientAlerts(rawData.pid);
              } else if (status === RESPONSE_STATUS.SENSOR_DATA) {
                const newValue =
                  rawData.unitCode && UNIT_CODES[rawData.unitCode]?.name === 'PERCENTAGE'
                    ? parseFloat(rawData.samples as string) * 100
                    : rawData.samples;

                if (rawData.sensorId) {
                  postNewSensorMetric(
                    rawData.sensorId,
                    rawData.code,
                    newValue,
                    rawData.unitCode ? UNIT_CODES[rawData.unitCode]?.display : undefined
                  );
                }
              } else if (status === RESPONSE_STATUS.BATTERY_STATUS) {
                const newValue = rawData.samples;

                if (rawData.sensorId) {
                  postNewSensorMetric(rawData.sensorId, rawData.code, newValue);
                }
              } else if (status === RESPONSE_STATUS.METRIC) {
                postNewMetric(
                  rawData.pid,
                  getMetricCode(rawData.code, rawData.deviceCode),
                  rawData.samples,
                  rawData.unitCode ? UNIT_CODES[rawData.unitCode]?.display : undefined,
                  rawData.timestamp?.toString()
                );
              }
            }
          };
          setWorkerReady(true);
        }
      }
    },
    [
      onNewRange,
      postNewMetric,
      postNewSensorMetric,
      postNewBedsideStatus,
      refetchBedGroups,
      refetchBeds,
      refetchMonitors,
      refetchSensors,
      quickRefetchSensors,
      refetchGroupAlerts,
      refetchAlertHistory,
      refreshToken,
      refreshTokenAndRestart,
      updateKeepAlive,
    ]
  );

  const terminateWorker = () => {
    if (workerRef && workerRef.current) {
      workerRef.current.terminate();
      workerRef.current = undefined;
    }
  };

  useEffect(() => {
    if (activeGroupId) {
      const patientIdentifiers: string[] = [];

      getActiveGroup().beds.forEach((bed) => {
        const associatedPatient = findAssociatedBedPatient(bed.id, beds.data);
        if (associatedPatient) patientIdentifiers.push(associatedPatient.patientPrimaryIdentifier);
      });
      groupPatientsIdentifiersRef.current = patientIdentifiers;
      workerRef.current?.postMessage({
        flow: WORKER_FLOWS.UPDATE_SELECTED_GROUP,
        patientsPrimaryIdentifiers: patientIdentifiers,
      });
    }
  }, [activeGroupId, beds.data, getActiveGroup]);

  useEffect(() => {
    // Triggers flow for the selected patient being updated when the selected bed/patient changes
    workerRef.current?.postMessage({
      flow: WORKER_FLOWS.UPDATE_SELECTED_PATIENT,
      patientPrimaryIdentifier: selectedPatientId,
    });
  }, [selectedPatientId]);

  return {
    socketCloseConnection,
    socketInitializer,
    startWorker,
    terminateWorker,
    workerReady,
  };
};

export default useMessageSocketHandler;
