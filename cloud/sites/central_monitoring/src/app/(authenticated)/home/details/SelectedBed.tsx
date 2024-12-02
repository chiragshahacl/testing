'use client';

import { usePatientMonitors } from '@/api/usePatientMonitors';
import TabPanel from '@/app/(authenticated)/home/details/Tabs/TabPanel';
import Loading from '@/app/loading';
import AlertGraphCard from '@/components/cards/AlertGraphCard';
import SensorCard from '@/components/cards/SensorCard/SensorCard';
import CloseIcon from '@/components/icons/CloseIcon';
import BedsideAudioAlarmStatusChip from '@/components/layout/AudioAlarmStatusChip';
import AlertList from '@/components/lists/AlertList';
import HorizontalListCustomItems from '@/components/lists/HorizontalListCustomItems';
import { StyledPatientInfoText } from '@/components/tabs/StyledTabs';
import { NO_ASSIGNED_VALUE } from '@/constants';
import useAudioAlerts from '@/hooks/useAudioAlerts';
import useMetrics from '@/hooks/useMetricsData';
import usePatientData from '@/hooks/usePatientsData';
import { Alert, DeviceAlert, VitalsAlert } from '@/types/alerts';
import { BedType } from '@/types/bed';
import { Metrics } from '@/types/metrics';
import { DisplayVitalsRange } from '@/types/patientMonitor';
import { Sensor, SensorStatus } from '@/types/sensor';
import { ALERT_PRIORITY, ALERT_TYPES, DEVICE_ALERT_CODES, WS_CODES } from '@/utils/metricCodes';
import { findAssociatedMonitor } from '@/utils/patientUtils';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';
import { get, partition as lodashPartition } from 'lodash';
import moment from 'moment';
import React, { useEffect, useMemo, useState } from 'react';
import { XyDataSeries } from 'scichart';
import EHRView from './EHR/EHRView';
import { EncounterStatus } from '@/types/encounters';
import { EHRStep } from '@/utils/ehr';
import MonitorNotAvailableModal from '@/components/modals/MonitorNotAvailableModal';
import { batteryStatusToBoolean } from '@/utils/sensorUtils';

interface SelectedBedProps {
  metrics?: Metrics;
  selectedBed: BedType;
  selectedBedGraphsWithData: string[];
  selectedTab: string | null;
  activeSensors: Sensor[];
  isLoading: boolean;
  alertThresholds: Record<string, DisplayVitalsRange>;
  alerts: Alert[];
  onTabSelected: (newTab: string) => void;
  sendNewDataSeries: (elementId: string, dataSeries?: XyDataSeries) => void;
  handleBackNavigation: () => void;
}

const SENSOR_FAILURE_ALERT_CODES = [
  DEVICE_ALERT_CODES.SENSOR_FAILURE_ALERT.code,
  DEVICE_ALERT_CODES.MODULE_FAILURE_ALERT.code,
  DEVICE_ALERT_CODES.SENSOR_ERROR_ALERT.code,
  DEVICE_ALERT_CODES.SYSTEM_ERROR_ALERT.code,
];

const EHRStepsForShowingMonitorNotAvailableModal = [
  EHRStep.CONFIRM_REQUEST,
  EHRStep.QUICK_ADMIT,
  EHRStep.SEARCH,
  EHRStep.SEARCH_RESULTS,
];

enum EHRMonitorNotAvailableMessageStatus {
  BED_SELECTION_START = 'BED_SELECTION_START',
  ALREADY_SHOWN = 'ALREADY_SHOWN',
  NOT_SHOWN = 'NOT_SHOWN',
}

const SelectedBed = ({
  metrics = {},
  selectedBed,
  selectedBedGraphsWithData,
  selectedTab,
  activeSensors,
  isLoading,
  alertThresholds = {},
  alerts,
  onTabSelected,
  sendNewDataSeries,
  handleBackNavigation,
}: SelectedBedProps) => {
  const [currentEHRStep, setCurrentEHRStep] = useState<EHRStep>(EHRStep.UNASSIGNED);
  const [ehrMonitorNotAvailableAccepted, setEhrMonitorNotAvailableAccepted] =
    useState<EHRMonitorNotAvailableMessageStatus>(
      EHRMonitorNotAvailableMessageStatus.BED_SELECTION_START
    );
  const { loadingSelectedBed } = usePatientData();
  const patientMonitors = usePatientMonitors();
  const theme = useTheme();
  const { sensorMetrics, bedsideStatus } = useMetrics();

  const hasAssociatedMonitor =
    findAssociatedMonitor(selectedBed.id || '', patientMonitors.data) !== NO_ASSIGNED_VALUE;

  const hasActivePatientSession =
    hasAssociatedMonitor &&
    !!selectedBed.patient?.patientId &&
    selectedBed.encounter?.status === EncounterStatus.IN_PROGRESS;

  const [vitalsAlerts, deviceAlerts] = useMemo(
    () => lodashPartition(alerts, (alertObject) => alertObject.type === ALERT_TYPES.VITALS),
    [alerts]
  ) as [VitalsAlert[], DeviceAlert[]];
  const audioAlerts = useAudioAlerts(vitalsAlerts);

  const { sensorFailureAlerts, sensorSignalAlerts, sensorOutOfRangeAlerts } = useMemo(() => {
    const newSensorFailureAlerts: Record<string, boolean> = {
      chest: false,
      adam: false,
      limb: false,
      nonin: false,
      bp: false,
      thermometer: false,
    };
    const newSensorSignalAlerts: Record<string, boolean> = {
      chest: false,
      adam: false,
      limb: false,
      nonin: false,
      bp: false,
      thermometer: false,
    };
    const newSensorOutOfRangeAlerts: Record<string, boolean> = {
      chest: false,
      adam: false,
      limb: false,
      nonin: false,
      bp: false,
      thermometer: false,
    };

    deviceAlerts
      .filter((deviceAlert) => SENSOR_FAILURE_ALERT_CODES.includes(deviceAlert.code))
      .forEach((deviceAlert) => {
        newSensorFailureAlerts[deviceAlert.deviceCode] = true;
      });

    deviceAlerts
      .filter(
        (deviceAlert: DeviceAlert) =>
          deviceAlert.code === DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code ||
          deviceAlert.code === DEVICE_ALERT_CODES.LOW_SIGNAL_ALERT.code
      )
      .forEach((deviceAlert) => {
        newSensorSignalAlerts[deviceAlert.deviceCode] = true;
      });

    deviceAlerts
      .filter(
        (deviceAlert: DeviceAlert) =>
          deviceAlert.code === DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code
      )
      .forEach((deviceAlert) => {
        newSensorOutOfRangeAlerts[deviceAlert.deviceCode] = true;
      });

    return {
      sensorFailureAlerts: newSensorFailureAlerts,
      sensorSignalAlerts: newSensorSignalAlerts,
      sensorOutOfRangeAlerts: newSensorOutOfRangeAlerts,
    };
  }, [deviceAlerts]);

  const associatedMonitor = useMemo(() => {
    return findAssociatedMonitor(selectedBed.id || '', patientMonitors.data);
  }, [selectedBed, patientMonitors.data]);

  const hasStartedEncounter = useMemo(
    () => selectedBed.encounter?.status === EncounterStatus.IN_PROGRESS,
    [selectedBed.encounter]
  );

  const hasMonitorNotAvailableAlert = useMemo(
    () =>
      deviceAlerts.find(
        (alert) => alert.code === DEVICE_ALERT_CODES.MONITOR_NOT_AVAILABLE_ALERT.code
      ),
    [deviceAlerts]
  );

  const showEHRMonitorNotAvailableModal = useMemo(() => {
    return (
      !hasActivePatientSession &&
      !!hasMonitorNotAvailableAlert &&
      ehrMonitorNotAvailableAccepted === EHRMonitorNotAvailableMessageStatus.NOT_SHOWN
    );
  }, [hasActivePatientSession, hasMonitorNotAvailableAlert, ehrMonitorNotAvailableAccepted]);

  useEffect(() => {
    // Manages if the Monitor Not Available Modal has already been shown should according
    // to current status of the EHR Patient admission flow
    if (EHRStepsForShowingMonitorNotAvailableModal.includes(currentEHRStep)) {
      if (!hasActivePatientSession && !hasMonitorNotAvailableAlert) {
        setEhrMonitorNotAvailableAccepted(EHRMonitorNotAvailableMessageStatus.NOT_SHOWN);
      } else {
        if (
          ehrMonitorNotAvailableAccepted === EHRMonitorNotAvailableMessageStatus.BED_SELECTION_START
        ) {
          setEhrMonitorNotAvailableAccepted(EHRMonitorNotAvailableMessageStatus.ALREADY_SHOWN);
        }
      }
    }
  }, [
    currentEHRStep,
    ehrMonitorNotAvailableAccepted,
    hasActivePatientSession,
    hasMonitorNotAvailableAlert,
  ]);

  return (
    <Grid
      display='flex'
      flexDirection='column'
      justifyContent='space-between'
      data-testid='selected-bed'
      flexGrow={1}
      py={0}
    >
      <MonitorNotAvailableModal
        isOpen={!!showEHRMonitorNotAvailableModal}
        onConfirm={() => {
          setEhrMonitorNotAvailableAccepted(EHRMonitorNotAvailableMessageStatus.ALREADY_SHOWN);
        }}
      />
      <Grid display='flex' flexDirection='row'>
        <Grid
          display='flex'
          flex={1}
          flexDirection='column'
          justifyContent='center'
          alignContent='center'
          alignItems={deviceAlerts.length > 0 || audioAlerts.length > 0 ? 'flex-start' : 'center'}
          py={10}
        >
          <Grid display='flex' flexDirection='row' alignItems='center' gap='8px'>
            <Typography variant='h2' sx={{ fontWeight: 500 }}>
              {`Bed ID ${selectedBed.bedNo || ''}`}
            </Typography>
            <BedsideAudioAlarmStatusChip status={bedsideStatus[associatedMonitor]} />
          </Grid>

          {findAssociatedMonitor(selectedBed.id || '', patientMonitors.data) === 'N/A' ? (
            <>
              <StyledPatientInfoText variant='h6'>-</StyledPatientInfoText>
              <StyledPatientInfoText variant='h6'>&nbsp;</StyledPatientInfoText>
            </>
          ) : (
            <>
              <StyledPatientInfoText variant='h6'>
                {hasStartedEncounter
                  ? `
                  ${selectedBed.patient?.patientLastName || ' - '} 
                  ${selectedBed.patient?.patientFirstName || ' - '}
                  ${
                    selectedBed.patient?.patientDob
                      ? `, ${moment.utc(selectedBed.patient.patientDob).format('yyyy-MM-DD')}`
                      : ''
                  }
                `
                  : ' - '}
              </StyledPatientInfoText>
              <Box display='flex'>
                <StyledPatientInfoText variant='h6' bold>
                  Patient Monitor ID
                </StyledPatientInfoText>
                <StyledPatientInfoText variant='h6'>
                  &nbsp;
                  {findAssociatedMonitor(selectedBed.id || '', patientMonitors.data, '-')}
                </StyledPatientInfoText>
              </Box>
            </>
          )}
        </Grid>
        <Grid
          sx={{
            position: 'absolute',
            right: 0,
            top: 0,
            width: '100%',
            justifyContent: 'flex-end',
            display: 'flex',
          }}
        >
          {deviceAlerts.length > 0 || audioAlerts.length > 0 ? (
            <AlertList
              deviceAlerts={deviceAlerts}
              vitalsAlerts={audioAlerts}
              containerStyles={{
                margin: theme.spacing(10, 0),
              }}
            />
          ) : null}
          <Grid
            display='flex'
            sx={{ minWidth: 48, cursor: 'pointer', margin: (theme) => theme.spacing(12, 0, 0, 50) }}
            onClick={handleBackNavigation}
          >
            <CloseIcon handleClick={handleBackNavigation} />
          </Grid>
        </Grid>
      </Grid>
      {loadingSelectedBed ? (
        <Loading />
      ) : hasMonitorNotAvailableAlert || !hasAssociatedMonitor ? (
        <AlertGraphCard
          priority={ALERT_PRIORITY.INTERNAL}
          alertMessage={DEVICE_ALERT_CODES.MONITOR_NOT_AVAILABLE_ALERT.waveformMessage}
          height='100%'
        />
      ) : !hasActivePatientSession ? (
        <EHRView
          selectedBed={selectedBed}
          currentStep={currentEHRStep}
          setCurrentStep={setCurrentEHRStep}
        />
      ) : (
        <Grid display='flex' flexDirection='column' flexGrow={1}>
          <Grid display='flex' flexDirection='row' minHeight={48} marginY={21}>
            <HorizontalListCustomItems>
              {activeSensors &&
                activeSensors.map((sensor, i) => (
                  <React.Fragment key={sensor.id}>
                    {i > 0 && (
                      <Box
                        key={`sensor_divider_${sensor.id}`}
                        sx={{
                          border: '0.5px solid #E0E0E0',
                          margin: (theme) => theme.spacing(8, 11.5),
                        }}
                      />
                    )}
                    <SensorCard
                      key={`sensor_${sensor.id}`}
                      title={sensor.title || ''}
                      id={sensor.primaryIdentifier || ''}
                      sensorType={sensor.type}
                      battery={
                        sensorOutOfRangeAlerts[sensor?.type]
                          ? undefined
                          : (get(
                              sensorMetrics,
                              `[${sensor.primaryIdentifier}][${WS_CODES.DEVICE_BATTERY}].value`,
                              undefined
                            ) as number | undefined)
                      }
                      signal={
                        get(
                          sensorMetrics,
                          `[${sensor.primaryIdentifier}][${WS_CODES.DEVICE_SIGNAL}].value`,
                          undefined
                        ) as number | undefined
                      }
                      status={
                        get(
                          sensorMetrics,
                          `[${sensor.primaryIdentifier}][${WS_CODES.DEVICE_STATUS}].value`,
                          undefined
                        ) as SensorStatus | undefined
                      }
                      charging={batteryStatusToBoolean(
                        get(
                          sensorMetrics[sensor.primaryIdentifier],
                          `[${WS_CODES.DEVICE_BATTERY_STATUS}]`,
                          undefined
                        )?.value as string
                      )}
                      alert={deviceAlerts.find((alert) => alert.deviceCode === sensor?.type)}
                      isLoading={isLoading}
                      hasSensorFailure={sensorFailureAlerts[sensor?.type] || false}
                      hasSensorSignalAlert={sensorSignalAlerts[sensor?.type] || false}
                    />
                  </React.Fragment>
                ))}
            </HorizontalListCustomItems>
          </Grid>
          <TabPanel
            selectedTab={selectedTab}
            onTabSelected={onTabSelected}
            selectedBed={selectedBed}
            selectedBedGraphsWithData={selectedBedGraphsWithData}
            metrics={metrics}
            sendNewDataSeries={sendNewDataSeries}
            activeSensors={activeSensors}
            isLoading={isLoading}
            alertThresholds={alertThresholds}
            hasActivePatientSession={hasActivePatientSession}
            vitalsAlerts={vitalsAlerts}
            deviceAlerts={deviceAlerts}
          />
        </Grid>
      )}
    </Grid>
  );
};

export default SelectedBed;
