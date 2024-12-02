'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';

import { useAllSensors } from '@/api/useAllSensors';
import { useBeds } from '@/api/useBeds';
import { useGroups } from '@/api/useGroups';
import { usePatientMonitors } from '@/api/usePatientMonitors';
import SelectedBed from '@/app/(authenticated)/home/details/SelectedBed';
import BedCard from '@/components/cards/BedCard';
import useAlerts from '@/hooks/useAlerts';
import useMetrics from '@/hooks/useMetricsData';
import usePatientData from '@/hooks/usePatientsData';
import useSession from '@/hooks/useSession';
import { Alert, AlertThresholds } from '@/types/alerts';
import { BedType } from '@/types/bed';
import { Sensor } from '@/types/sensor';
import { DEVICE_ALERT_CODES } from '@/utils/metricCodes';
import { findAssociatedMonitor, findAssociatedMonitorRanges } from '@/utils/patientUtils';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { get } from 'lodash';
import { XyDataSeries } from 'scichart';

interface DetailsProps {
  navigateToMultipatient: () => void;
  setupFinished: boolean;
  currentPatientGraphsWithData: string[];
  sensorsByBed: Record<string, Sensor[]>;
  sendNewDataSeries: (elementId: string, dataSeries?: XyDataSeries) => void;
  onResetData: () => void;
}

/**
 * Screen for showing the full data of a single bed/patient, and monitor basic vitals and alerts
 * for other beds/patients in the same group. Designed for a max of 16 beds in a single group
 */
const Details = ({
  navigateToMultipatient,
  setupFinished,
  currentPatientGraphsWithData,
  sensorsByBed,
  sendNewDataSeries,
  onResetData,
}: DetailsProps) => {
  /* --------- STATE AND CONTEXTS START --------- */
  const { accessToken } = useSession();
  const [selectedTab, setSelectedTab] = useState<string | null>(null);
  const [alertThresholds, setAlertThresholds] = useState<AlertThresholds>({});

  const {
    getActiveGroup,
    activeGroupId,
    selectedBed,
    resetMonitorsKeepAlive,
    updateKeepAlive,
    updateSelectedBed,
  } = usePatientData();

  /* --------- STATE AND CONTEXTS END --------- */

  const patientMonitors = usePatientMonitors();
  const beds = useBeds();
  const bedGroups = useGroups();
  const apiSensors = useAllSensors(activeGroupId);
  const { alertsByBed, alertsByPatient } = useAlerts(activeGroupId);
  const { metrics } = useMetrics();

  /* --------- DATA HANDLING START --------- */
  const resetData = useCallback(() => {
    resetMonitorsKeepAlive();
    onResetData();
    if (activeGroupId) {
      const newAlertThresholds: AlertThresholds = {};
      getActiveGroup().beds.forEach((originalBed: BedType) => {
        const bedData = beds.data.find((bed) => bed.id === originalBed.id);
        if (bedData) {
          // Set vitals limits for patients
          newAlertThresholds[bedData.id] = findAssociatedMonitorRanges(
            bedData.id,
            patientMonitors.data
          );

          // Update freshnes of monitor data
          const monitorId = findAssociatedMonitor(bedData.id, patientMonitors.data, '');

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
      setAlertThresholds(newAlertThresholds);
    }
  }, [
    activeGroupId,
    beds.data,
    getActiveGroup,
    patientMonitors.data,
    resetMonitorsKeepAlive,
    updateKeepAlive,
  ]);

  const checkSelectedBed = useCallback(() => {
    // Check if current bed is part of the current group
    const activeGroup = getActiveGroup();

    // Set Selected Bed
    const isSelectedBedInGroup =
      activeGroup.beds.findIndex((bed: BedType) => bed.id === selectedBed?.id) >= 0;
    if (activeGroup.beds.length === 0) {
      updateSelectedBed('');
    } else if (!selectedBed?.id || !isSelectedBedInGroup) {
      updateSelectedBed(activeGroup.beds[0].id);
    }
  }, [getActiveGroup, selectedBed?.id, updateSelectedBed]);

  /* --------- DATA HANDLING END --------- */

  /* --------- EFFECTS START --------- */

  useEffect(() => {
    // Checks if selected bed still exists after bedGroups update
    if (bedGroups.data.length > 0) {
      checkSelectedBed();
    }
  }, [bedGroups.data, checkSelectedBed]);

  useEffect(() => {
    // Sets selected bed as default if there is no selected bed or if the selected bed is not part
    // of the selected group
    if (!selectedBed?.id && activeGroupId) {
      const activeGroupBeds = getActiveGroup().beds;
      if (activeGroupBeds.length > 0) {
        updateSelectedBed(activeGroupBeds[0].id);
      }
    }
  }, [activeGroupId, selectedBed]);

  useEffect(() => {
    // Sets the alert ranges for the patients
    const newAlertThresholds: AlertThresholds = {};
    getActiveGroup().beds.forEach((bed: BedType) => {
      newAlertThresholds[bed.id] = findAssociatedMonitorRanges(bed.id, patientMonitors.data);
    });
    setAlertThresholds(newAlertThresholds);
  }, [getActiveGroup, patientMonitors.data]);

  useEffect(() => {
    // Updates selected bed when setup is fully finished and when the group changes
    if (accessToken && activeGroupId && setupFinished) {
      checkSelectedBed();
      resetData();
    }
  }, [activeGroupId, accessToken, setupFinished]);

  /* --------- EFFECTS END --------- */

  /* --------- CONSTANTS ----------- */

  const bedsById: Record<string, BedType> = useMemo(
    () =>
      beds.data.reduce<Record<string, BedType>>(
        (newValue, bed) => ({ ...newValue, [bed.id]: bed }),
        {}
      ),
    [beds.data]
  );

  const selectedPatientId = useMemo(() => {
    return get(selectedBed, 'patient.patientPrimaryIdentifier', null);
  }, [selectedBed]);

  const selectedBedAlerts = useMemo(() => {
    let result: Alert[] = [];
    if (selectedBed?.id) {
      result = selectedPatientId
        ? [
            ...get(alertsByPatient, `[${selectedPatientId}]`, []),
            ...get(alertsByBed, `[${selectedBed.id}]`, []),
          ]
        : [...get(alertsByBed, `[${selectedBed.id}]`, [])];
    }
    return result;
  }, [alertsByBed, alertsByPatient, selectedBed?.id, selectedPatientId]);

  /* --------- END CONSTANTS ----------- */

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
    <Grid
      container
      display='flex'
      flexDirection='row'
      sx={{ backgroundColor: 'disabled', height: '100%' }}
    >
      <Grid
        container
        direction='column'
        flexWrap='wrap'
        gap={9.43}
        padding={(theme) => theme.spacing(12, 6, 12, 12)}
        width={activeGroupId && getActiveGroup().beds?.length > 8 ? 465 : 232.5}
        maxHeight='100vh'
      >
        {activeGroupId
          ? getActiveGroup().beds?.map((originalBed: BedType) => {
              const bedData = bedsById[originalBed.id];
              const pid = get(bedData, 'patient.patientPrimaryIdentifier', '');
              return (
                bedData && (
                  <BedCard
                    key={bedData.id}
                    bedId={bedData.id}
                    title={bedData.bedNo}
                    metrics={metrics[pid]}
                    alertThresholds={alertThresholds[bedData.id] || {}}
                    alerts={[
                      ...get(alertsByPatient, `[${pid}]`, []),
                      ...get(alertsByBed, `[${bedData.id}]`, []),
                    ]}
                    activeSensors={sensorsByBed[bedData.id] || []}
                    hasAssociatedMonitor={
                      findAssociatedMonitor(bedData?.id, patientMonitors.data) !== 'N/A'
                    }
                    encounterStatus={bedData?.encounter?.status}
                    isLoading={apiSensors.isLoading}
                  />
                )
              );
            })
          : null}
      </Grid>
      <Grid
        flex={1}
        display='flex'
        padding={8}
        sx={{ backgroundColor: 'background.modal', flexDirection: 'column' }}
        position='relative'
      >
        {!selectedBed && <Typography variant='overline'>No bed selected</Typography>}

        {selectedBed && selectedBed.id ? (
          <SelectedBed
            key={selectedBed.id}
            metrics={selectedPatientId ? metrics[selectedPatientId] : undefined}
            selectedBed={selectedBed}
            selectedBedGraphsWithData={currentPatientGraphsWithData}
            selectedTab={selectedTab}
            onTabSelected={setSelectedTab}
            sendNewDataSeries={sendNewDataSeries}
            activeSensors={sensorsByBed[selectedBed.id || ''] || []}
            isLoading={apiSensors.isLoading}
            handleBackNavigation={navigateToMultipatient}
            alertThresholds={alertThresholds[selectedBed.id] || {}}
            alerts={selectedBedAlerts}
          />
        ) : (
          <Typography variant='overline'>No data for selected patient</Typography>
        )}
      </Grid>
    </Grid>
  );
};

export default Details;
