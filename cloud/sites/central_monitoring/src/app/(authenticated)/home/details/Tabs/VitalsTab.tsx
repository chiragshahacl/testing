'use client';

import Graph from '@/app/(authenticated)/home/details/Metrics/Graphs/Graph';
import HeartRate from '@/app/(authenticated)/home/details/Metrics/HeartRate';
import Oximeter from '@/app/(authenticated)/home/details/Metrics/Oximeter';
import PerfusionIndex from '@/app/(authenticated)/home/details/Metrics/PerfusionIndex';
import RespiratoryPulseRate from '@/app/(authenticated)/home/details/Metrics/RespiratoryPulseRate';
import RespiratoryRate from '@/app/(authenticated)/home/details/Metrics/RespiratoryRate';
import VitalMetricsPanel from '@/app/(authenticated)/home/details/VitalMetricsPanel';
import {
  HR_TEXT_COLOR,
  NO_CHEST_SENSOR_MESSAGE,
  NO_OXIMETER_MESSAGE,
  RR_TEXT_COLOR,
  SPO_TEXT_COLOR,
} from '@/constants';
import useSensorsConnected from '@/hooks/useSensorsConnected';
import useTechnicalAlerts from '@/hooks/useTechnicalAlerts';
import { DeviceAlert, VitalsAlert } from '@/types/alerts';
import { BedType } from '@/types/bed';
import { ChartType } from '@/types/charts';
import {
  HeartRateUnit,
  Metrics,
  OximeterUnit,
  PerfusionIndexUnit,
  PulseRateUnit,
} from '@/types/metrics';
import { DisplayVitalsRange } from '@/types/patientMonitor';
import { SENSOR_TYPES, Sensor } from '@/types/sensor';
import { getDeviceAlert, getHighestPriorityWaveformAlert } from '@/utils/alertUtils';
import {
  ALERT_PRIORITY,
  DEVICE_CODES,
  METRIC_INTERNAL_CODES,
  RANGES_CODES,
  VITALS_ALERT_CODES,
  VitalMetricInternalCodes,
  WS_CODES,
} from '@/utils/metricCodes';
import { SafeParser } from '@/utils/safeParser';
import Grid from '@mui/material/Grid';
import { useMemo } from 'react';
import { XyDataSeries } from 'scichart';

interface VitalsTabProps {
  selectedBed: BedType;
  metrics?: Metrics;
  sendNewDataSeries: (metric: string, dataseries?: XyDataSeries) => void;
  vitalsAlerts: VitalsAlert[];
  deviceAlerts: DeviceAlert[];
  activeSensors: Sensor[];
  isLoading: boolean;
  alertThresholds?: Record<string, DisplayVitalsRange>;
  graphsWithData?: Array<string>;
  hasActivePatientSession: boolean;
}

const VitalsTab = ({
  selectedBed,
  hasActivePatientSession,
  metrics = {},
  alertThresholds = {},
  sendNewDataSeries,
  vitalsAlerts,
  deviceAlerts,
  activeSensors,
  isLoading,
  graphsWithData = [WS_CODES.ECG, WS_CODES.PLETH, WS_CODES.RR],
}: VitalsTabProps) => {
  const technicalAlerts = useTechnicalAlerts(deviceAlerts);

  const sensorsConnected = useSensorsConnected(activeSensors, hasActivePatientSession);

  const vitalsAlertSeverities: Record<VitalMetricInternalCodes, ALERT_PRIORITY | undefined> =
    useMemo(
      () => ({
        [METRIC_INTERNAL_CODES.HR]: vitalsAlerts.find(
          (alert) =>
            alert.code === VITALS_ALERT_CODES.HR_HIGH_VISUAL.code ||
            alert.code === VITALS_ALERT_CODES.HR_LOW_VISUAL.code
        )?.priority,
        [METRIC_INTERNAL_CODES.SPO2]: vitalsAlerts.find(
          (alert) =>
            alert.code === VITALS_ALERT_CODES.SPO2_HIGH_VISUAL.code ||
            alert.code === VITALS_ALERT_CODES.SPO2_LOW_VISUAL.code
        )?.priority,
        [METRIC_INTERNAL_CODES.PR]: vitalsAlerts.find(
          (alert) =>
            alert.code === VITALS_ALERT_CODES.PR_HIGH_VISUAL.code ||
            alert.code === VITALS_ALERT_CODES.PR_LOW_VISUAL.code
        )?.priority,
        [METRIC_INTERNAL_CODES.RR_METRIC]: vitalsAlerts.find(
          (alert) =>
            alert.code === VITALS_ALERT_CODES.RR_HIGH_VISUAL.code ||
            alert.code === VITALS_ALERT_CODES.RR_LOW_VISUAL.code
        )?.priority,
        [METRIC_INTERNAL_CODES.NIBP]: vitalsAlerts.find(
          (alert) =>
            alert.code === VITALS_ALERT_CODES.SYS_HIGH_VISUAL.code ||
            alert.code === VITALS_ALERT_CODES.SYS_LOW_VISUAL.code ||
            alert.code === VITALS_ALERT_CODES.DIA_HIGH_VISUAL.code ||
            alert.code === VITALS_ALERT_CODES.DIA_LOW_VISUAL.code
        )?.priority,
        [METRIC_INTERNAL_CODES.BODY_TEMP]: vitalsAlerts.find(
          (alert) =>
            alert.code === VITALS_ALERT_CODES.BODY_TEMP_HIGH_VISUAL.code ||
            alert.code === VITALS_ALERT_CODES.BODY_TEMP_LOW_VISUAL.code
        )?.priority,
        [METRIC_INTERNAL_CODES.CHEST_TEMP]: vitalsAlerts.find(
          (alert) =>
            (alert.code === VITALS_ALERT_CODES.CHEST_TEMP_LOW_VISUAL.code ||
              alert.code === VITALS_ALERT_CODES.CHEST_TEMP_HIGH_VISUAL.code) &&
            (alert.deviceCode === SENSOR_TYPES.CHEST || alert.deviceCode === SENSOR_TYPES.ADAM)
        )?.priority,
        [METRIC_INTERNAL_CODES.LIMB_TEMP]: vitalsAlerts.find(
          (alert) =>
            (alert.code === VITALS_ALERT_CODES.LIMB_TEMP_LOW_VISUAL.code ||
              alert.code === VITALS_ALERT_CODES.LIMB_TEMP_HIGH_VISUAL.code) &&
            alert.deviceCode === SENSOR_TYPES.LIMB
        )?.priority,
        [METRIC_INTERNAL_CODES.FALLS]: vitalsAlerts.find(
          (alert) => alert.code === VITALS_ALERT_CODES.FALL_VISUAL.code
        )?.priority,
        [METRIC_INTERNAL_CODES.POSITION]: vitalsAlerts.find(
          (alert) => alert.code === VITALS_ALERT_CODES.POSITION_VISUAL.code
        )?.priority,
      }),
      [vitalsAlerts]
    );

  const {
    ecgHasAlertSeverity,
    ecgAlertMessage,
    plethHasAlertSeverity,
    plethAlertMessage,
    rrHasTechnicalAlertSeverity,
    rrAlertMessage,
  } = useMemo(() => {
    const waveformAlerts: DeviceAlert[] = deviceAlerts
      .map((alertObj) => ({
        ...alertObj,
        waveformMessage: getDeviceAlert(alertObj.code, alertObj.deviceCode as SENSOR_TYPES)
          ?.waveformMessage,
      }))
      .filter(({ waveformMessage }) => !!waveformMessage);

    const anneChestDeviceAlert = getHighestPriorityWaveformAlert(
      waveformAlerts.filter((alert) => alert.deviceCode === DEVICE_CODES.ANNE_CHEST.type)
    );
    const noninDeviceAlert = getHighestPriorityWaveformAlert(
      waveformAlerts.filter((alert) => alert.deviceCode === DEVICE_CODES.NONIN_3150.type)
    );
    const anneLimbDeviceAlert = getHighestPriorityWaveformAlert(
      waveformAlerts.filter((alert) => alert.deviceCode === DEVICE_CODES.ANNE_LIMB.type)
    );

    return {
      ecgHasAlertSeverity:
        !isLoading && sensorsConnected[METRIC_INTERNAL_CODES.ECG]
          ? anneChestDeviceAlert?.priority
          : ALERT_PRIORITY.INTERNAL,
      ecgAlertMessage:
        !isLoading && sensorsConnected[METRIC_INTERNAL_CODES.ECG]
          ? anneChestDeviceAlert?.waveformMessage
          : NO_CHEST_SENSOR_MESSAGE,
      plethHasAlertSeverity:
        !isLoading && sensorsConnected[METRIC_INTERNAL_CODES.PLETH]
          ? noninDeviceAlert?.priority || anneLimbDeviceAlert?.priority
          : ALERT_PRIORITY.INTERNAL,
      plethAlertMessage:
        !isLoading && sensorsConnected[METRIC_INTERNAL_CODES.PLETH]
          ? noninDeviceAlert?.waveformMessage || anneLimbDeviceAlert?.waveformMessage
          : NO_OXIMETER_MESSAGE,
      rrHasTechnicalAlertSeverity:
        !isLoading && sensorsConnected[METRIC_INTERNAL_CODES.RR]
          ? anneChestDeviceAlert?.priority
          : ALERT_PRIORITY.INTERNAL,
      rrAlertMessage:
        !isLoading && sensorsConnected[METRIC_INTERNAL_CODES.RR]
          ? anneChestDeviceAlert?.waveformMessage
          : NO_CHEST_SENSOR_MESSAGE,
    };
  }, [deviceAlerts, sensorsConnected, isLoading]);

  // ------------ MEMOIZED VALUES END ------------
  return (
    <Grid data-testid='vitals-tab' display='flex' flexDirection='column' gap={8}>
      <Grid display='flex' flexDirection='row' minHeight={236}>
        <Graph
          height={228}
          chartType={ChartType.ECG}
          color={HR_TEXT_COLOR}
          alertPriority={ecgHasAlertSeverity}
          alertMessage={ecgAlertMessage}
          bed={selectedBed}
          hasData={graphsWithData.includes(WS_CODES.ECG)}
          onUpdate={(dataSeries?: XyDataSeries) => {
            sendNewDataSeries(WS_CODES.ECG, dataSeries);
          }}
        />

        <HeartRate
          alertPriority={vitalsAlertSeverities[METRIC_INTERNAL_CODES.HR]}
          unit={metrics[METRIC_INTERNAL_CODES.HR]?.unit as HeartRateUnit}
          threshold={alertThresholds[RANGES_CODES.HR]}
          isConnected={sensorsConnected[METRIC_INTERNAL_CODES.HR]}
          isLoading={isLoading || metrics[METRIC_INTERNAL_CODES.HR]?.value === undefined}
          isError={
            !hasActivePatientSession ||
            technicalAlerts.HR ||
            metrics[METRIC_INTERNAL_CODES.HR]?.value === null
          }
          value={SafeParser.toFixed(metrics[METRIC_INTERNAL_CODES.HR]?.value)}
        />
      </Grid>
      <Grid display='flex' flexDirection='row' minHeight={210}>
        <Graph
          height={202}
          chartType={ChartType.PLETH}
          color={SPO_TEXT_COLOR}
          alertPriority={plethHasAlertSeverity}
          alertMessage={plethAlertMessage}
          bed={selectedBed}
          hasData={graphsWithData.includes(WS_CODES.PLETH)}
          onUpdate={(dataSeries?: XyDataSeries) => {
            sendNewDataSeries(WS_CODES.PLETH, dataSeries);
          }}
          activeSensors={activeSensors}
        />
        <Grid flex={1} flexDirection='column' className='metricCard' gap={8}>
          <Oximeter
            alertPriority={vitalsAlertSeverities[METRIC_INTERNAL_CODES.SPO2]}
            unit={metrics[METRIC_INTERNAL_CODES.SPO2]?.unit as OximeterUnit}
            threshold={alertThresholds[RANGES_CODES.SPO2]}
            isConnected={sensorsConnected[METRIC_INTERNAL_CODES.SPO2]}
            isLoading={isLoading || metrics[METRIC_INTERNAL_CODES.SPO2]?.value === undefined}
            isError={
              !hasActivePatientSession ||
              technicalAlerts.SPO ||
              metrics[METRIC_INTERNAL_CODES.SPO2]?.value === null
            }
            value={SafeParser.toFixed(metrics[METRIC_INTERNAL_CODES.SPO2]?.value)}
          />
          <RespiratoryPulseRate
            alertPriority={vitalsAlertSeverities[METRIC_INTERNAL_CODES.PR]}
            unit={metrics[METRIC_INTERNAL_CODES.PR]?.unit as PulseRateUnit}
            threshold={alertThresholds[RANGES_CODES.PR]}
            isConnected={sensorsConnected[METRIC_INTERNAL_CODES.PR]}
            isLoading={isLoading || metrics[METRIC_INTERNAL_CODES.PR]?.value === undefined}
            isError={
              !hasActivePatientSession ||
              technicalAlerts.PR ||
              metrics[METRIC_INTERNAL_CODES.PR]?.value === null
            }
            value={SafeParser.toFixed(metrics[METRIC_INTERNAL_CODES.PR]?.value)}
          />
          <PerfusionIndex
            isConnected={sensorsConnected[METRIC_INTERNAL_CODES.PI]}
            isLoading={isLoading || metrics[METRIC_INTERNAL_CODES.PI]?.value === undefined}
            unit={metrics[METRIC_INTERNAL_CODES.PI]?.unit as PerfusionIndexUnit}
            isError={
              !hasActivePatientSession ||
              technicalAlerts.PI ||
              metrics[METRIC_INTERNAL_CODES.PI]?.value === null
            }
            value={SafeParser.toFixed(metrics[METRIC_INTERNAL_CODES.PI]?.value, 1)}
          />
        </Grid>
      </Grid>
      <Grid display='flex' flexDirection='row' minHeight={72}>
        <Graph
          height={64}
          chartType={ChartType.RR}
          color={RR_TEXT_COLOR}
          alertPriority={rrHasTechnicalAlertSeverity}
          bed={selectedBed}
          onUpdate={(dataSeries?: XyDataSeries) => {
            sendNewDataSeries(WS_CODES.RR, dataSeries);
          }}
          hasData={graphsWithData.includes(WS_CODES.RR)}
          alertMessage={rrAlertMessage}
        />
        <RespiratoryRate
          alertPriority={vitalsAlertSeverities[METRIC_INTERNAL_CODES.RR_METRIC]}
          isConnected={sensorsConnected[METRIC_INTERNAL_CODES.RR_METRIC]}
          threshold={alertThresholds[RANGES_CODES.RR]}
          value={SafeParser.toFixed(metrics[METRIC_INTERNAL_CODES.RR_METRIC]?.value)}
          isLoading={isLoading || metrics[METRIC_INTERNAL_CODES.RR_METRIC]?.value === undefined}
          isError={
            !hasActivePatientSession ||
            technicalAlerts.RR_METRIC ||
            metrics[METRIC_INTERNAL_CODES.RR_METRIC]?.value === null
          }
        />
      </Grid>

      {/* Lower Line */}
      <VitalMetricsPanel
        hasActivePatientSession={hasActivePatientSession}
        metrics={metrics}
        alertThresholds={alertThresholds}
        vitalsAlertSeverities={vitalsAlertSeverities}
        technicalAlerts={technicalAlerts}
        isLoading={isLoading}
        activeSensors={activeSensors}
      />
    </Grid>
  );
};

export default VitalsTab;
