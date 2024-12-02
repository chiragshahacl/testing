/* eslint-disable no-case-declarations */
'use client';

import { useAllSensors } from '@/api/useAllSensors';
import { useBeds } from '@/api/useBeds';
import { useGroups } from '@/api/useGroups';
import { usePatientMonitors } from '@/api/usePatientMonitors';
import Loading from '@/app/loading';
import GraphCard, { SHOW_TEXT } from '@/components/graph/GraphCard';
import NoDataBed from '@/components/graph/NoDataBed';
import { NO_ASSIGNED_VALUE } from '@/constants';
import useAlerts from '@/hooks/useAlerts';
import useMetrics from '@/hooks/useMetricsData';
import usePatientData from '@/hooks/usePatientsData';
import useSession from '@/hooks/useSession';
import useTypedSearchParams from '@/hooks/useTypedSearchParams';
import { AlertThresholds } from '@/types/alerts';
import { BedType } from '@/types/bed';
import { ChartType } from '@/types/charts';
import { EncounterStatus } from '@/types/encounters';
import { DisplayVitalsRange, PatientMonitor } from '@/types/patientMonitor';
import { SENSOR_TYPES } from '@/types/sensor';
import { isMonitorNotAvailableAlertPresent } from '@/utils/alertUtils';
import { DEVICE_ALERT_CODES, METRIC_INTERNAL_CODES } from '@/utils/metricCodes';
import { findAssociatedMonitor, findAssociatedMonitorRanges } from '@/utils/patientUtils';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { get } from 'lodash';
import { useEffect, useMemo, useState } from 'react';
import { XyDataSeries } from 'scichart';

interface MultipatientProps {
  navigateToDetails: () => void;
  setupFinished: boolean;
  patientsWithData: string[];
  sendNewDataSeries: (elementId: string, dataSeries?: XyDataSeries) => void;
  onResetData: () => void;
}

/**
 * Screen for showing HR and ECG data, as well as alerts, for all patients inside a single group.
 * Designed for a max of 16 beds in a single group
 */
const Multipatient = ({
  navigateToDetails,
  setupFinished,
  patientsWithData,
  sendNewDataSeries,
  onResetData,
}: MultipatientProps) => {
  /* --------- STATE AND CONTEXTS START --------- */
  const searchParams = useTypedSearchParams();
  const [triggeredInitialSetup, setTriggeredInitialSetup] = useState<boolean>(false);
  const [alertThresholds, setAlertThresholds] = useState<
    Record<string, Record<string, DisplayVitalsRange>>
  >({});

  const { accessToken } = useSession();

  const {
    getActiveGroup,
    activeGroupId,
    updateActiveGroup,
    resetMonitorsKeepAlive,
    updateKeepAlive,
    updateSelectedBed,
  } = usePatientData();

  /* --------- STATE AND CONTEXTS END --------- */

  /* --------- API CALLS START --------- */

  const patientMonitors = usePatientMonitors();
  const allSensors = useAllSensors(activeGroupId);
  const beds = useBeds();
  const { metrics, resetMetrics } = useMetrics();
  const { alertsByBed, alertsByPatient } = useAlerts(activeGroupId);

  const bedGroups = useGroups();

  const { bedsWithChestSensor, bedsWithHrSensor } = useMemo(() => {
    if (
      beds.data?.length > 0 &&
      patientMonitors.data?.length > 0 &&
      allSensors.data?.sensors.length > 0
    ) {
      const bedsWithChestSensor: Record<string, boolean> = {};
      const bedsWithHrSensor: Record<string, boolean> = {};

      patientMonitors.data.forEach((patientMonitor: PatientMonitor) => {
        const bedSensors = allSensors.data?.sensors?.filter(
          (sensor) => sensor.patientMonitorId === patientMonitor.id
        );

        if (patientMonitor?.assignedBedId) {
          if (bedSensors.find((sensor) => sensor.type === SENSOR_TYPES.CHEST)) {
            bedsWithChestSensor[patientMonitor.assignedBedId] = true;
            bedsWithHrSensor[patientMonitor.assignedBedId] = true;
          } else {
            bedsWithChestSensor[patientMonitor.assignedBedId] = false;
            bedsWithHrSensor[patientMonitor.assignedBedId] = !!bedSensors.find(
              (sensor) => sensor.type === SENSOR_TYPES.ADAM
            );
          }
        }
      });
      return {
        bedsWithChestSensor,
        bedsWithHrSensor,
      };
    }
    return { bedsWithChestSensor: {}, bedsWithHrSensor: {} };
  }, [beds.data, patientMonitors.data, allSensors.data]);

  /* --------- API CALLS END --------- */

  /* --------- DATA HANDLING START --------- */

  const resetData = () => {
    resetMonitorsKeepAlive();
    onResetData();
    resetMetrics();
    if (activeGroupId) {
      getActiveGroup().beds.forEach(({ id }: BedType) => {
        const bedData = beds.data?.find((bed) => bed.id === id);
        if (bedData !== undefined) {
          const monitorId = findAssociatedMonitor(id, patientMonitors.data, '');

          if (monitorId) {
            const foundMonitor = patientMonitors.data.find(
              (monitor) => monitor.monitorId === monitorId
            );
            if (
              !foundMonitor?.alerts.find(
                (alert) => alert.code === DEVICE_ALERT_CODES.MONITOR_NOT_AVAILABLE_ALERT.code
              )
            )
              updateKeepAlive(monitorId);
          }
        }
      });
    }
  };

  const handlePageSetup = () => {
    if (accessToken) {
      resetData();
    }
  };

  const handleNavigateToDetails = (bedId: string) => {
    updateSelectedBed(bedId);
    navigateToDetails();
  };

  const selectDefaultGroup = () => {
    if (!bedGroups.isPlaceholderData && bedGroups.isSuccess && bedGroups?.data?.length > 0) {
      const defaultGroup = searchParams.groupIndex;
      if (defaultGroup) {
        if (bedGroups.data.length > defaultGroup) {
          updateActiveGroup(bedGroups.data[defaultGroup].id);
        }
      }
    }
  };

  /* --------- DATA HANDLING END --------- */

  /* --------- EFFECTS START --------- */

  useEffect(() => {
    // Starts page setup flow
    if (!triggeredInitialSetup && setupFinished) {
      selectDefaultGroup();
      setTriggeredInitialSetup(true);
    }
  }, [triggeredInitialSetup, setupFinished]);

  useEffect(() => {
    // Clears data and starts socket connection on first start and if accessToken is updated
    if (accessToken && (setupFinished || searchParams.hideSetup)) {
      handlePageSetup();
    }
  }, [accessToken, setupFinished]);

  useEffect(() => {
    // Sets the alert ranges for the patients
    const newAlertThresholds: AlertThresholds = {};
    beds.data.forEach((bed: BedType) => {
      newAlertThresholds[bed.id] = findAssociatedMonitorRanges(bed.id, patientMonitors.data);
    });
    setAlertThresholds(newAlertThresholds);
  }, [patientMonitors.data, beds.data]);

  /* --------- EFFECTS END --------- */

  if (beds.isFetching) {
    return (
      <Grid display='flex' height='90%' justifyContent='center' alignItems='center'>
        <Loading />
      </Grid>
    );
  }

  if (beds.isError) {
    return (
      <Grid display='flex' height='90%' justifyContent='center' alignItems='center'>
        <Typography variant='overline' textAlign='center' textTransform='uppercase'>
          FAILED TO DISPLAY BEDS, PLEASE CONTACT SERVICE
        </Typography>
      </Grid>
    );
  }

  return (
    <div className='container' data-testid='active-group-beds'>
      {activeGroupId
        ? getActiveGroup().beds.map(({ id }: BedType, index: number, bedsArray: BedType[]) => {
            const bedData = beds.data?.find((bed) => bed.id === id);
            if (!bedData) return null;
            const pid = bedData.patient?.patientPrimaryIdentifier;

            if (findAssociatedMonitor(bedData.id, patientMonitors.data) === NO_ASSIGNED_VALUE)
              return (
                // Shows patient monitor unavailable message
                <NoDataBed
                  key={bedData.bedNo}
                  bedNo={bedData.bedNo}
                  onClick={() => {
                    handleNavigateToDetails(bedData.id);
                  }}
                />
              );
            let alerts = [...get(alertsByBed, `[${bedData.id}]`, [])];
            if (pid) alerts = alerts.concat(get(alertsByPatient, `[${pid}]`, []));
            const bedAmount = getActiveGroup().beds.length;
            const monitorNotAvailable = isMonitorNotAvailableAlertPresent(alerts);
            return (
              <Grid
                key={bedData.bedNo}
                className='column'
                sx={{
                  backgroundColor: 'primary.dark',
                  borderRadius: 16,
                  width: '49%',
                  cursor: 'pointer',
                }}
                onClick={() => {
                  handleNavigateToDetails(bedData.id);
                }}
                data-testid='graph-card-container'
              >
                <GraphCard
                  key={`ecg_${bedData.bedNo}_${activeGroupId}`}
                  showAlerts
                  bedData={{ ...bedData }}
                  metrics={pid ? get(metrics, `[${pid}]`) : undefined}
                  metric={METRIC_INTERNAL_CODES.ECG}
                  chartType={ChartType.ECG}
                  hasChestSensorConnected={!!bedsWithChestSensor[bedData.id]}
                  showText={
                    bedData.patient?.patientPrimaryIdentifier &&
                    bedData.encounter?.status === EncounterStatus.IN_PROGRESS &&
                    (bedsWithChestSensor[bedData.id] || bedsWithHrSensor[bedData.id]) &&
                    !monitorNotAvailable
                      ? SHOW_TEXT.ALL
                      : SHOW_TEXT.BED_INFO
                  }
                  hasDataLoaded={
                    !!pid && patientsWithData.indexOf(pid) >= 0 && !bedGroups.isFetching
                  }
                  elementId={`ecg_${index}`}
                  sendUpdateCallback={sendNewDataSeries}
                  maxHeight={bedsArray.length > 8 ? '100%' : bedsArray.length > 4 ? 177 : 236}
                  smallView={bedsArray.length > 8}
                  alertThresholds={alertThresholds[bedData.id] || {}}
                  alerts={alerts}
                  showSummary={bedsWithChestSensor[bedData.id] || bedsWithHrSensor[bedData.id]}
                  hasActivePatientSession={
                    !!pid && bedData.encounter?.status === EncounterStatus.IN_PROGRESS
                  }
                  showScale
                  shiftScaleRight={bedAmount > 8}
                  doubleColumn={bedAmount > 2}
                  fullSizeScale={bedAmount > 8}
                  reducedRange={bedAmount > 4}
                />
              </Grid>
            );
          })
        : null}
    </div>
  );
};

export default Multipatient;
