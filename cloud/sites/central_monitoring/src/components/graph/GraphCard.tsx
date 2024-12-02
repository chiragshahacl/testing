import AlertList from '@/components/lists/AlertList';
import { NO_CHEST_SENSOR_MESSAGE } from '@/constants';
import useAudioAlerts from '@/hooks/useAudioAlerts';
import useTechnicalAlerts from '@/hooks/useTechnicalAlerts';
import { Alert, DeviceAlert, VitalsAlert } from '@/types/alerts';
import { BedType } from '@/types/bed';
import { ChartLocation, ChartType } from '@/types/charts';
import { Metrics } from '@/types/metrics';
import { DisplayVitalsRange } from '@/types/patientMonitor';
import { getHighestPriorityAlertColor, getHighestPriorityWaveformAlert } from '@/utils/alertUtils';
import { getChartColor, getPointsLoopPerGraph } from '@/utils/graphUtils';
import {
  ALERT_PRIORITY,
  ALERT_TYPES,
  DEVICE_ALERT_CODES,
  METRIC_INTERNAL_CODES,
  METRIC_SENSOR_MAP,
  RANGES_CODES,
  VITALS_ALERT_CODES,
} from '@/utils/metricCodes';
import { SafeParser } from '@/utils/safeParser';
import Grid from '@mui/material/Grid';
import { styled } from '@mui/material/styles';
import { get, partition as lodashPartition } from 'lodash';
import React, { useEffect, useMemo } from 'react';
import {
  EAutoRange,
  ENumericFormat,
  FastLineRenderableSeries,
  NumberRange,
  NumericAxis,
  SciChartSurface,
  TSciChart,
  XyDataSeries,
} from 'scichart';
import AlertGraphCard from '../cards/AlertGraphCard';
import GraphInfo from './GraphInfo';
import GraphSummary from './GraphSummary';
import { SENSOR_TYPES } from '@/types/sensor';
import ECGScaleIndicator from './ECGScaleIndicator';
import { EncounterStatus } from '@/types/encounters';
import moment from 'moment';
import { getCachedRuntimeConfig } from '@/utils/runtime';

const GraphElement = styled('div')(() => ({
  width: '100%',
}));

export enum SHOW_TEXT {
  ALL = 'all',
  BED_INFO = 'bedInfo',
  METRIC_NAME = 'metricName',
}

interface GraphCardProps {
  bedData: BedType;
  metrics?: Metrics;
  elementId: string;
  metric?: METRIC_INTERNAL_CODES;
  color?: string;
  showText: SHOW_TEXT;
  showAlerts?: boolean;
  smallView?: boolean;
  chartType: ChartType;
  maxHeight?: string | number;
  containerStyles?: React.CSSProperties;
  alertThresholds?: Record<string, DisplayVitalsRange>;
  alerts?: Alert[];
  sendUpdateCallback: (elementId: string, dataSeries?: XyDataSeries) => void;
  hasChestSensorConnected?: boolean;
  hasDataLoaded?: boolean;
  showSummary?: boolean;
  hasActivePatientSession?: boolean;
  showScale?: boolean;
  shiftScaleRight?: boolean;
  doubleColumn?: boolean;
  fullSizeScale?: boolean;
  reducedRange?: boolean;
  sensorType?: SENSOR_TYPES;
}

const generateGraph = async (elementId: string) => {
  const { sciChartSurface: surface, wasmContext: context } = await SciChartSurface.create(
    elementId,
    { disableAspect: false }
  );

  return { surface, context };
};

const ECGYAxisOptionsStandard = {
  autoRange: EAutoRange.Never,
  isVisible: false,
  visibleRange: new NumberRange(-2.4, 2.4),
};

const ECGYAxisOptionsMediumRange = {
  autoRange: EAutoRange.Never,
  isVisible: false,
  visibleRange: new NumberRange(-1.8, 1.8),
};

const ECGYAxisOptionsSmallRange = {
  autoRange: EAutoRange.Never,
  isVisible: false,
  visibleRange: new NumberRange(-0.196, 1),
};

const GenericYAxisOptions = {
  autoRange: EAutoRange.Always,
  isVisible: false,
};

const HOSPITAL_TIMEZONE = getCachedRuntimeConfig().HOSPITAL_TZ ?? 'UTC';

const GraphCard = ({
  bedData,
  metrics = {},
  elementId,
  metric = undefined,
  hasChestSensorConnected = true,
  hasDataLoaded = true,
  showText,
  showAlerts,
  maxHeight,
  smallView = false,
  chartType,
  alertThresholds = {},
  alerts = [],
  showSummary = false,
  sendUpdateCallback,
  hasActivePatientSession = false,
  showScale = false,
  shiftScaleRight = true,
  doubleColumn = false,
  fullSizeScale = false,
  reducedRange = false,
  sensorType = undefined,
}: GraphCardProps) => {
  const [vitalsAlerts, deviceAlerts] = useMemo(
    () => lodashPartition(alerts, (alertObject) => alertObject.type === ALERT_TYPES.VITALS),
    [alerts]
  ) as [VitalsAlert[], DeviceAlert[]];
  const audioAlerts = useAudioAlerts(vitalsAlerts);
  const technicalAlerts = useTechnicalAlerts(deviceAlerts);

  const hrVisualAlerts = useMemo(
    () =>
      vitalsAlerts.filter(
        (alert) =>
          alert.code === VITALS_ALERT_CODES.HR_LOW_VISUAL.code ||
          alert.code === VITALS_ALERT_CODES.HR_HIGH_VISUAL.code
      ),
    [vitalsAlerts]
  );

  const patientMonitorAvailable = useMemo(
    () =>
      !deviceAlerts.find(
        (alert) => alert.code === DEVICE_ALERT_CODES.MONITOR_NOT_AVAILABLE_ALERT.code
      ),
    [deviceAlerts]
  );

  const waveformError: { priority: string; message: string; secondLine?: string } | undefined =
    useMemo(() => {
      if (!patientMonitorAvailable) {
        return {
          priority: ALERT_PRIORITY.INTERNAL,
          // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
          message: DEVICE_ALERT_CODES.MONITOR_NOT_AVAILABLE_ALERT.waveformMessage!,
        };
      }

      if (!hasActivePatientSession) {
        const encounterStatus = get(bedData, 'encounter.status');
        if (encounterStatus === EncounterStatus.PLANNED) {
          const encounterDate = bedData.encounter?.createdAt;
          return {
            priority: ALERT_PRIORITY.INTERNAL,
            message: 'PENDING CONFIRMATION',
            secondLine: `SENT ${moment
              .tz(encounterDate, 'UTC')
              .tz(HOSPITAL_TIMEZONE)
              .format('MM-DD-yyyy HH:mm')}`,
          };
        } else if (encounterStatus === EncounterStatus.CANCELLED)
          return {
            priority: ALERT_PRIORITY.INTERNAL,
            message: 'ADMISSION REJECTED - NO ACTIVE PATIENT SESSION',
            secondLine: 'SELECT TO ADMIT PATIENT',
          };
        else
          return {
            priority: ALERT_PRIORITY.INTERNAL,
            message: 'NO ACTIVE PATIENT SESSION',
            secondLine: 'SELECT TO ADMIT PATIENT',
          };
      }

      const highestPriorityWaveformAlert =
        showAlerts &&
        metric &&
        getHighestPriorityWaveformAlert(
          deviceAlerts.filter((alertObj) =>
            METRIC_SENSOR_MAP[metric].includes(alertObj.deviceCode as SENSOR_TYPES)
          )
        );

      if (highestPriorityWaveformAlert)
        return {
          priority:
            vitalsAlerts.length > 0
              ? ALERT_PRIORITY.INTERNAL
              : highestPriorityWaveformAlert.priority,
          message: highestPriorityWaveformAlert.waveformMessage || '',
        };
    }, [
      hasActivePatientSession,
      patientMonitorAvailable,
      showAlerts,
      metric,
      deviceAlerts,
      vitalsAlerts.length,
    ]);

  const configureSurface = (surface: SciChartSurface, context: TSciChart) => {
    surface.background = 'transparent';
    const xAxis = new NumericAxis(context, { autoRange: EAutoRange.Once, isVisible: false });
    surface.xAxes.add(xAxis);

    const yAxis = new NumericAxis(
      context,
      chartType === ChartType.ECG
        ? reducedRange
          ? fullSizeScale
            ? ECGYAxisOptionsSmallRange
            : ECGYAxisOptionsMediumRange
          : ECGYAxisOptionsStandard
        : GenericYAxisOptions
    );
    yAxis.labelProvider.numericFormat = ENumericFormat.Decimal;
    surface.yAxes.add(yAxis);
  };

  const setupChart = async () => {
    // Generate Graph Elements
    const { surface, context } = await generateGraph(elementId);
    configureSurface(surface, context);
    const pointsInGraph = getPointsLoopPerGraph(
      chartType,
      doubleColumn
        ? ChartLocation.MULTI_PATIENT_DOUBLE_COLUMN
        : ChartLocation.MULTI_PATIENT_SINGLE_COLUMN,
      sensorType
    );

    // Create and fill initial data series
    const dataSeries = new XyDataSeries(context);
    const xArray = Array.from({ length: pointsInGraph }, (_, i) => i);
    const yArray = Array(pointsInGraph).fill(NaN);

    dataSeries.appendRange(xArray, yArray);

    surface.renderableSeries.add(
      new FastLineRenderableSeries(context, {
        strokeThickness: window.screen.height > 1080 ? 5 : 2,
        stroke: getChartColor(chartType),
        dataSeries,
      })
    );
    sendUpdateCallback(bedData.patient?.patientPrimaryIdentifier ?? '', dataSeries);
  };

  useEffect(() => {
    // Setups chart if load has finished and no waveform errors are present
    // Removes the dataseries from parent component if there is an error or if still loading
    if (hasChestSensorConnected && hasDataLoaded && !waveformError) void setupChart();
    else {
      sendUpdateCallback(bedData.patient?.patientPrimaryIdentifier ?? '');
    }
  }, [hasChestSensorConnected, hasDataLoaded, waveformError]);

  return (
    <Grid
      key={bedData.id}
      className='column'
      data-testid={`graph-card-${vitalsAlerts.length > 0 ? 'with' : 'without'}-vitals-alert`}
      sx={{
        padding: (theme) => theme.spacing(4, 24, 4, 12),
        backgroundColor:
          vitalsAlerts.length > 0 && patientMonitorAvailable ? 'secondary.main' : 'primary.dark',
        borderRadius: 16,
        position: 'relative',
        height: '100%',
        display: 'flex',
      }}
    >
      <GraphInfo data={bedData} metric={metric} showText={showText} />
      {showAlerts && (
        <AlertList
          deviceAlerts={deviceAlerts}
          vitalsAlerts={audioAlerts}
          containerStyles={{
            position: 'absolute',
            top: 0,
            right: 0,
            borderRadius: '0 16px 0 0',
          }}
        />
      )}
      <Grid
        sx={{
          display: 'flex',
          flex: 1,
          flexDirection: 'row',
          alignItems: 'center',
        }}
      >
        <Grid
          sx={{
            display: 'flex',
            flex: 4,
            flexDirection: 'row',
            position: 'relative',
            height: maxHeight ? maxHeight : undefined,
          }}
        >
          {hasChestSensorConnected && hasDataLoaded && !waveformError && (
            <GraphElement
              id={`${elementId}`}
              data-testid={`graph-${elementId}`}
              style={maxHeight ? { maxHeight } : {}}
            />
          )}
          {showScale &&
            hasChestSensorConnected &&
            hasDataLoaded &&
            !waveformError &&
            chartType === ChartType.ECG && (
              <ECGScaleIndicator
                customHeight={fullSizeScale ? '70%' : undefined}
                shiftScaleRight={shiftScaleRight}
              />
            )}
          {waveformError ? (
            <Grid flex={1} justifyContent='center'>
              <AlertGraphCard
                priority={waveformError.priority as ALERT_PRIORITY}
                alertMessage={waveformError.message}
                secondLineAlertMessage={waveformError.secondLine}
                height='100%'
                textBg='primary.dark'
              />
            </Grid>
          ) : (
            <>
              {!hasChestSensorConnected && (
                <Grid flex={1} justifyContent='center'>
                  <AlertGraphCard
                    priority={ALERT_PRIORITY.INTERNAL}
                    alertMessage={NO_CHEST_SENSOR_MESSAGE}
                    height='100%'
                    textBg='primary.dark'
                  />
                </Grid>
              )}
            </>
          )}
        </Grid>
        {showSummary && hasActivePatientSession && patientMonitorAvailable && (
          <Grid
            sx={{
              display: 'flex',
              flex: 1,
              flexDirection: 'row',
              justifyContent: 'right',
              height: '100%',
            }}
          >
            <GraphSummary
              data={{
                hr:
                  !hasActivePatientSession ||
                  waveformError ||
                  technicalAlerts.HR ||
                  metrics[METRIC_INTERNAL_CODES.HR]?.value === null
                    ? '-?-'
                    : SafeParser.toFixed(metrics[METRIC_INTERNAL_CODES.HR]?.value),
                highLimit: alertThresholds[RANGES_CODES.HR]?.upperLimit,
                lowLimit: alertThresholds[RANGES_CODES.HR]?.lowerLimit,
              }}
              smallView={smallView}
              alertColor={
                hrVisualAlerts.length > 0 ? getHighestPriorityAlertColor(hrVisualAlerts) : '#00C868'
              }
            />
          </Grid>
        )}
      </Grid>
    </Grid>
  );
};

export default GraphCard;
