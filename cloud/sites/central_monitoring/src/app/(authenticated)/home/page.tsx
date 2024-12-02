/* eslint-disable no-case-declarations */
'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import Details from './details/Details';
import Multipatient from './multipatient/Multipatient';
import useMessageSocketHandler from '@/hooks/useMessageSocketHandler';
import { WS_CODES } from '@/utils/metricCodes';
import useAlerts from '@/hooks/useAlerts';
import usePatientData from '@/hooks/usePatientsData';
import { getCachedRuntimeConfig } from '@/utils/runtime';
import useSession from '@/hooks/useSession';
import { useBeds } from '@/api/useBeds';
import { useGroups } from '@/api/useGroups';
import { useAllSensors } from '@/api/useAllSensors';
import { SocketWorkerMessage } from '@/types/socketMessage';
import {
  getPLETHGraphRelatedSensor,
  getPointsLoopPerGraph,
  getValuesFromData,
  transformWsCodeToChartType,
  updateDataseries,
} from '@/utils/graphUtils';
import { Sensor } from '@/types/sensor';
import { XyDataSeries } from 'scichart';
import { ChartLocation, ChartType } from '@/types/charts';
import { PatientPrimaryID } from '@/types/patient';
import { usePatientMonitors } from '@/api/usePatientMonitors';
import useNetwork from '@/hooks/useNetwork';
import useAudioManager from '@/hooks/useAudioManager';
import {
  checkAudioAlertsExist,
  filterAlertsByBedInGroup,
  filterAlertsByPatientInGroup,
} from '@/utils/alertUtils';

enum HomeScreens {
  MULTIPATIENT = 'MULTIPATIENT',
  DETAILS = 'DETAILS',
}

const GRAPHS = [WS_CODES.ECG, WS_CODES.PLETH, WS_CODES.RR];

// We can't use React States within the worker callbacks (they lose context), so we need to save
// some data the regular JS way
let socketCurrentScreen: HomeScreens = HomeScreens.MULTIPATIENT; // Stores the current screen being shown
let currentPatient: string | null = null; // Stores the id of the current patient
let hasReceivedData: Record<PatientPrimaryID, boolean> = {}; // Stores if each patient has received data

/**
 * Screen for showing HR and ECG data, as well as alerts, for all patients inside a single group.
 * Designed for a max of 16 beds in a single group
 */
const Home = () => {
  /* --------- STATE AND CONTEXTS START --------- */
  const [currentScreen, setCurrentScreen] = useState<HomeScreens>(HomeScreens.MULTIPATIENT);
  const [setupFinished, setSetupFinished] = useState<boolean>(false);

  const { startWorker, socketCloseConnection, socketInitializer, workerReady } =
    useMessageSocketHandler([WS_CODES.HR, WS_CODES.SPO2, WS_CODES.ECG]);
  const { accessToken } = useSession();
  const { activeGroupId, getActiveGroup, selectedBed } = usePatientData();
  const { resetAlertsForPatient } = useAlerts(activeGroupId);
  const beds = useBeds();
  const bedGroups = useGroups();
  const apiSensors = useAllSensors(activeGroupId);
  const patientMonitors = usePatientMonitors();
  const networkIsOnline = useNetwork();
  const { setActiveAlertsExist, setAudioAlert, stopAlertSound } = useAudioManager();
  const { alertsByBed, alertsByPatient } = useAlerts(activeGroupId);

  // Details View Persistent Data
  const [currentPatientGraphsWithData, setCurrentPatientGraphsWithData] = useState<string[]>([]);
  const [sensors, setSensors] = useState<Sensor[]>([]);

  const bedIdByPatientMonitor: Record<string, string | null> = useMemo(
    () =>
      patientMonitors.data.reduce<Record<string, string | null>>(
        (newValue, { id, assignedBedId }) => ({ ...newValue, [id]: assignedBedId }),
        {}
      ),
    [patientMonitors.data]
  );

  const sensorsByBed: Record<string, Sensor[]> = useMemo(() => {
    const newSensorsByBed: Record<string, Sensor[]> = {};

    sensors.forEach((sensor) => {
      const bedId = bedIdByPatientMonitor[sensor.patientMonitorId];
      if (bedId) {
        if (!newSensorsByBed[bedId]) {
          newSensorsByBed[bedId] = [];
        }
        newSensorsByBed[bedId].push(sensor);
      }
    });

    return newSensorsByBed;
  }, [sensors, bedIdByPatientMonitor]);

  const currentPointsByMetric = useRef<Record<string, number>>({});
  const currentBedSensors = useRef<Sensor[]>([]);
  const dataSeriesByMetric = useRef<Record<string, XyDataSeries | undefined>>({});

  // MultiPatient view Peristent Data
  const [patientsWithData, setPatientsWithData] = useState<string[]>([]);

  const currentPointsByPatient = useRef<Record<PatientPrimaryID, number>>({});
  const dataSeriesByPatient = useRef<Record<PatientPrimaryID, XyDataSeries>>({});

  /* --------- STATE AND CONTEXTS END --------- */

  /* --------- DATA HANDLING START --------- */

  const onResetData = () => {
    // Reset details info
    GRAPHS.forEach((graphCode: string) => {
      currentPointsByMetric.current[graphCode] = 0;
    });
    setCurrentPatientGraphsWithData([]);
    currentPointsByMetric.current = {};
    dataSeriesByMetric.current = {};

    // Reset multipatient info
    hasReceivedData = {};
    setPatientsWithData([]);
    currentPointsByPatient.current = {};
    dataSeriesByPatient.current = {};
  };

  const onResetPatientAlerts = (pid: string) => {
    resetAlertsForPatient(pid);
  };

  const navigateToDetails = () => {
    setCurrentScreen(HomeScreens.DETAILS);
    socketCurrentScreen = HomeScreens.DETAILS;
  };

  const navigateToMultipatient = () => {
    setCurrentScreen(HomeScreens.MULTIPATIENT);
    socketCurrentScreen = HomeScreens.MULTIPATIENT;
  };

  const newDetailsDataSeries = (elementId: string, dataSeries?: XyDataSeries) => {
    dataSeriesByMetric.current[elementId] = dataSeries;
  };

  const newMultipatientDataSeries = (elementId: string, dataSeries?: XyDataSeries) => {
    if (dataSeries) dataSeriesByPatient.current[elementId] = dataSeries;
  };

  const handleReceivedNewPatientData = () => {
    const allPatientIds = Object.keys(hasReceivedData);
    const newPwD = allPatientIds.filter(function (pid) {
      return hasReceivedData[pid];
    });
    setPatientsWithData(newPwD);
  };

  const onWaveformData = (code: string, pid: string, rawData: SocketWorkerMessage) => {
    if (socketCurrentScreen === HomeScreens.DETAILS) {
      if (pid === currentPatient) {
        setCurrentPatientGraphsWithData((previousGraphsWithData) => {
          if (!previousGraphsWithData.includes(code)) {
            return [...previousGraphsWithData, code];
          }
          return previousGraphsWithData;
        });

        const samples = rawData.samples as (number | null)[];
        let currentPoint = currentPointsByMetric.current[code];
        const dataSeries = dataSeriesByMetric.current[code];
        const chartType = transformWsCodeToChartType(code);

        if (isNaN(currentPoint)) {
          currentPointsByMetric.current[code] = 0;
          currentPoint = 0;
        }

        if (chartType) {
          const { xArr: xArr0, xPlusGapArr: xPlusGapArr0 } = getValuesFromData(
            currentPoint,
            samples.length,
            getPointsLoopPerGraph(
              chartType,
              ChartLocation.DETAILS,
              getPLETHGraphRelatedSensor(currentBedSensors.current)
            )
          );
          currentPointsByMetric.current[code] += samples.length;

          if (dataSeries) {
            updateDataseries(samples, dataSeries, xArr0, xPlusGapArr0);
          }
        }
      }
    } else if (currentScreen === HomeScreens.MULTIPATIENT) {
      if (code === WS_CODES.ECG) {
        if (!hasReceivedData[pid]) {
          hasReceivedData[pid] = true;
          handleReceivedNewPatientData();
        }
        const samples = rawData.samples as (number | null)[];
        let currentPoint = currentPointsByPatient.current[pid];
        const dataSeries = dataSeriesByPatient.current[pid];

        if (isNaN(currentPoint)) {
          currentPointsByPatient.current[pid] = 0;
          currentPoint = 0;
        }

        const { xArr: xArr0, xPlusGapArr: xPlusGapArr0 } = getValuesFromData(
          currentPoint,
          samples.length,
          getPointsLoopPerGraph(
            ChartType.ECG,
            getActiveGroup().beds.length > 2
              ? ChartLocation.MULTI_PATIENT_DOUBLE_COLUMN
              : ChartLocation.MULTI_PATIENT_SINGLE_COLUMN
          )
        );
        currentPointsByPatient.current[pid] += samples.length;
        if (dataSeries) {
          updateDataseries(samples, dataSeries, xArr0, xPlusGapArr0);
        }
      }
    }
  };

  /* --------- DATA HANDLING END --------- */

  /* --------- EFFECTS START --------- */

  useEffect(() => {
    // Starts WS WebWorker when the component is mounted
    startWorker(onResetPatientAlerts, onWaveformData);

    return socketCloseConnection;
  }, []);

  useEffect(() => {
    if (selectedBed?.id) {
      // Reset the graph's loading state
      setCurrentPatientGraphsWithData([]);

      // Updates which is the main bed
      if (selectedBed.patient) {
        currentPatient = selectedBed.patient?.patientPrimaryIdentifier;
      }
    }
  }, [activeGroupId, selectedBed, beds.data]);

  useEffect(() => {
    // Sets setupFinished as true when API requests have completed
    if (workerReady && !apiSensors.isLoading && !beds.isLoading && !bedGroups.isLoading) {
      setSetupFinished(true);
    }
  }, [workerReady, apiSensors.data, apiSensors.isLoading, beds.isLoading, bedGroups.isLoading]);

  useEffect(() => {
    // Start socket when setup is finish and restart if active group changes
    if (accessToken && activeGroupId && setupFinished) {
      socketCloseConnection();
      const ignoreEcgFilter = parseInt(getCachedRuntimeConfig().IGNORE_BUTTERWORTH_FILTERS);

      // TODO: Remove ignoreEcgFilter param when ECG Scale Indicator has been tested
      socketInitializer(!!ignoreEcgFilter);
    }
  }, [activeGroupId, accessToken, setupFinished]);

  // Add sensors of current bed to a ref so it can be accessed on onWaveformData
  useEffect(() => {
    if (selectedBed) currentBedSensors.current = sensorsByBed[selectedBed.id] || [];
    else currentBedSensors.current = [];
  }, [sensorsByBed, selectedBed]);

  useEffect(() => {
    // The sensors can be obtained from the API or the web socket, so we need a separate state with the sensors
    if (apiSensors.isSuccess && apiSensors.data) {
      setSensors(apiSensors.data.sensors);
    }
  }, [apiSensors.isSuccess, apiSensors.data]);

  useEffect(() => {
    // Triggers audio alerts (or triggers audio stop) when alerts are updated or when
    // network connection is lost/regained
    if (networkIsOnline) {
      const allAlerts = [
        ...filterAlertsByPatientInGroup(alertsByPatient, getActiveGroup().beds, beds.data),
        ...filterAlertsByBedInGroup(alertsByBed, getActiveGroup().beds),
      ];
      if (checkAudioAlertsExist(allAlerts)) {
        setAudioAlert(Object.values(allAlerts).flat());
        setActiveAlertsExist(true);
      } else {
        stopAlertSound();
      }
    }
  }, [
    activeGroupId,
    alertsByPatient,
    alertsByBed,
    networkIsOnline,
    getActiveGroup,
    beds.data,
    setAudioAlert,
    setActiveAlertsExist,
    stopAlertSound,
  ]);

  /* --------- EFFECTS END --------- */

  if (currentScreen === HomeScreens.DETAILS) {
    return (
      <Details
        navigateToMultipatient={navigateToMultipatient}
        setupFinished={setupFinished}
        currentPatientGraphsWithData={currentPatientGraphsWithData}
        sensorsByBed={sensorsByBed}
        sendNewDataSeries={newDetailsDataSeries}
        onResetData={onResetData}
      />
    );
  }

  return (
    <Multipatient
      navigateToDetails={navigateToDetails}
      setupFinished={setupFinished}
      patientsWithData={patientsWithData}
      sendNewDataSeries={newMultipatientDataSeries}
      onResetData={onResetData}
    />
  );
};

export default Home;
