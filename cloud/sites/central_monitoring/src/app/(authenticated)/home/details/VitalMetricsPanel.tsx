import BloodPressure from '@/app/(authenticated)/home/details/Metrics/BloodPressure';
import BodyPosition from '@/app/(authenticated)/home/details/Metrics/BodyPosition';
import BodyTemperature from '@/app/(authenticated)/home/details/Metrics/BodyTemperature';
import ChestTemperature from '@/app/(authenticated)/home/details/Metrics/ChestTemperature';
import FallDetector from '@/app/(authenticated)/home/details/Metrics/FallDetector';
import LimbTemperature from '@/app/(authenticated)/home/details/Metrics/LimbTemperature';
import PulseRate from '@/app/(authenticated)/home/details/Metrics/PulseRate';
import useSensorsConnected from '@/hooks/useSensorsConnected';
import {
  BloodPressureUnit,
  FallState,
  Metrics,
  PulseRateUnit,
  TemperatureUnit,
} from '@/types/metrics';
import { DisplayVitalsRange } from '@/types/patientMonitor';
import { Sensor } from '@/types/sensor';
import { TECHNICAL_ALERT_TYPE } from '@/utils/alertUtils';
import {
  ALERT_PRIORITY,
  METRIC_INTERNAL_CODES,
  POSITION_TYPES,
  RANGES_CODES,
  VitalMetricInternalCodes,
} from '@/utils/metricCodes';
import { SafeParser } from '@/utils/safeParser';
import Grid from '@mui/material/Grid';
import moment from 'moment';
import { useEffect, useMemo, useState } from 'react';

type VitalMetricsPanelProps = {
  hasActivePatientSession?: boolean;
  metrics?: Metrics;
  alertThresholds?: Record<string, DisplayVitalsRange>;
  vitalsAlertSeverities: Record<VitalMetricInternalCodes, ALERT_PRIORITY | undefined>;
  technicalAlerts: Record<TECHNICAL_ALERT_TYPE, boolean>;
  isLoading: boolean;
  activeSensors: Sensor[];
};

const VitalMetricsPanel = ({
  hasActivePatientSession = true,
  metrics = {},
  alertThresholds = {},
  vitalsAlertSeverities,
  technicalAlerts,
  isLoading,
  activeSensors,
}: VitalMetricsPanelProps) => {
  const [hoursInCurrentPosition, setHoursInCurrentPosition] = useState<string>(
    moment.utc(0).format('HH')
  );
  const [minutesInCurrentPosition, setMinutesInCurrentPosition] = useState<string>(
    moment.utc(0).format('mm')
  );

  const sensorsConnected = useSensorsConnected(activeSensors, hasActivePatientSession);

  useEffect(() => {
    // Updates the time for the position duration when a new duration value is received
    const positionDuration = parseInt(
      metrics[METRIC_INTERNAL_CODES.POSITION_DURATION]?.value as string
    );
    if (positionDuration) {
      if (positionDuration >= 100 * 60) {
        // We cap the shown time to 100 hours
        setHoursInCurrentPosition('99');
        setMinutesInCurrentPosition('59');
      } else {
        setHoursInCurrentPosition(
          Math.floor(positionDuration / 60).toLocaleString('en-US', { minimumIntegerDigits: 2 })
        );
        setMinutesInCurrentPosition(
          Math.floor(positionDuration % 60).toLocaleString('en-US', { minimumIntegerDigits: 2 })
        );
      }
    } else {
      setHoursInCurrentPosition('00');
      setMinutesInCurrentPosition('00');
    }
  }, [metrics[METRIC_INTERNAL_CODES.POSITION_DURATION]?.value]);

  const fallState = useMemo((): FallState | null => {
    if (!hasActivePatientSession || technicalAlerts.FALLS) {
      return FallState.UNKNOWN;
    }
    if (!sensorsConnected[METRIC_INTERNAL_CODES.FALLS] && !isLoading) {
      return null;
    }
    if (metrics[METRIC_INTERNAL_CODES.FALLS]?.value === 0) {
      return FallState.NOT_DETECTED;
    }
    if (!metrics[METRIC_INTERNAL_CODES.FALLS]?.value) {
      return FallState.UNKNOWN;
    }
    if ((metrics[METRIC_INTERNAL_CODES.FALLS]?.value as number) > 0) {
      return FallState.DETECTED;
    }
    return FallState.UNKNOWN;
  }, [hasActivePatientSession, technicalAlerts, sensorsConnected, metrics, isLoading]);

  return (
    <Grid display='flex' flexDirection='row'>
      <Grid display='flex' flex={4.75} flexDirection='row' mr={10} gap={10}>
        <PulseRate
          isConnected={sensorsConnected[METRIC_INTERNAL_CODES.PULSE]}
          isLoading={isLoading}
          timestamp={metrics[METRIC_INTERNAL_CODES.PULSE]?.timestamp}
          unit={metrics[METRIC_INTERNAL_CODES.PULSE]?.unit as PulseRateUnit}
          measurement={{
            value: SafeParser.toFixed(metrics[METRIC_INTERNAL_CODES.PULSE]?.value),
          }}
          measureFailed={technicalAlerts.PULSE}
          isError={
            !hasActivePatientSession ||
            technicalAlerts.PULSE ||
            metrics[METRIC_INTERNAL_CODES.PULSE]?.value === null
          }
        />
        <BloodPressure
          unit={
            (metrics[METRIC_INTERNAL_CODES.DIA]?.unit ||
              metrics[METRIC_INTERNAL_CODES.SYS]?.unit) as BloodPressureUnit
          }
          alertPriority={vitalsAlertSeverities[METRIC_INTERNAL_CODES.NIBP]}
          isConnected={sensorsConnected[METRIC_INTERNAL_CODES.NIBP]}
          timestamp={
            metrics[METRIC_INTERNAL_CODES.SYS]?.timestamp ||
            metrics[METRIC_INTERNAL_CODES.DIA]?.timestamp
          }
          isLoading={isLoading}
          measureFailed={technicalAlerts.NIBP}
          systolicError={
            !hasActivePatientSession ||
            technicalAlerts.NIBP ||
            metrics[METRIC_INTERNAL_CODES.SYS]?.value === null
          }
          diastolicError={
            !hasActivePatientSession ||
            technicalAlerts.NIBP ||
            metrics[METRIC_INTERNAL_CODES.DIA]?.value === null
          }
          systolicMeasurement={{
            value: SafeParser.toFixed(metrics[METRIC_INTERNAL_CODES.SYS]?.value),
            upperLimit: alertThresholds[RANGES_CODES.SYS]?.upperLimit?.toString(),
            lowerLimit: alertThresholds[RANGES_CODES.SYS]?.lowerLimit?.toString(),
          }}
          diastolicMeasurement={{
            value: SafeParser.toFixed(metrics[METRIC_INTERNAL_CODES.DIA]?.value),
            upperLimit: alertThresholds[RANGES_CODES.DIA]?.upperLimit?.toString(),
            lowerLimit: alertThresholds[RANGES_CODES.DIA]?.lowerLimit?.toString(),
          }}
          mapMeasurement={SafeParser.toFixed(metrics[METRIC_INTERNAL_CODES.MAP]?.value)}
          mapError={
            !hasActivePatientSession ||
            technicalAlerts.NIBP ||
            metrics[METRIC_INTERNAL_CODES.MAP]?.value === null
          }
        />
        <BodyTemperature
          alertPriority={vitalsAlertSeverities[METRIC_INTERNAL_CODES.BODY_TEMP]}
          unit={
            (metrics[METRIC_INTERNAL_CODES.BODY_TEMP]?.unit ||
              metrics[METRIC_INTERNAL_CODES.CHEST_TEMP]?.unit ||
              metrics[METRIC_INTERNAL_CODES.LIMB_TEMP]?.unit) as TemperatureUnit
          }
          timestamp={metrics[METRIC_INTERNAL_CODES.BODY_TEMP]?.timestamp}
          isLoading={isLoading}
          isConnected={sensorsConnected[METRIC_INTERNAL_CODES.BODY_TEMP]}
          isError={
            !hasActivePatientSession ||
            technicalAlerts.BODY_TEMP ||
            metrics[METRIC_INTERNAL_CODES.BODY_TEMP]?.value === null
          }
          measurement={{
            value: SafeParser.toFixed(metrics[METRIC_INTERNAL_CODES.BODY_TEMP]?.value, 1),
            upperLimit: SafeParser.toFixed(
              alertThresholds[RANGES_CODES.TEMPERATURE_BODY]?.upperLimit,
              1
            ),
            lowerLimit: SafeParser.toFixed(
              alertThresholds[RANGES_CODES.TEMPERATURE_BODY]?.lowerLimit,
              1
            ),
          }}
        />
        <ChestTemperature
          alertPriority={vitalsAlertSeverities[METRIC_INTERNAL_CODES.CHEST_TEMP]}
          unit={
            (metrics[METRIC_INTERNAL_CODES.CHEST_TEMP]?.unit ||
              metrics[METRIC_INTERNAL_CODES.LIMB_TEMP]?.unit ||
              metrics[METRIC_INTERNAL_CODES.BODY_TEMP]?.unit) as TemperatureUnit
          }
          isConnected={sensorsConnected[METRIC_INTERNAL_CODES.CHEST_TEMP]}
          isLoading={isLoading}
          isError={
            !hasActivePatientSession ||
            technicalAlerts.CHEST_TEMP ||
            metrics[METRIC_INTERNAL_CODES.CHEST_TEMP]?.value === null
          }
          measurement={{
            value: SafeParser.toFixed(metrics[METRIC_INTERNAL_CODES.CHEST_TEMP]?.value, 1),
            upperLimit: SafeParser.toFixed(
              alertThresholds[RANGES_CODES.TEMPERATURE_SKIN]?.upperLimit,
              1
            ),
            lowerLimit: SafeParser.toFixed(
              alertThresholds[RANGES_CODES.TEMPERATURE_SKIN]?.lowerLimit,
              1
            ),
          }}
        />
        <LimbTemperature
          isConnected={sensorsConnected[METRIC_INTERNAL_CODES.LIMB_TEMP]}
          alertPriority={vitalsAlertSeverities[METRIC_INTERNAL_CODES.LIMB_TEMP]}
          isLoading={isLoading}
          isError={
            !hasActivePatientSession ||
            technicalAlerts.LIMB_TEMP ||
            metrics[METRIC_INTERNAL_CODES.LIMB_TEMP]?.value === null
          }
          measurement={{
            value: SafeParser.toFixed(metrics[METRIC_INTERNAL_CODES.LIMB_TEMP]?.value, 1),
            upperLimit: SafeParser.toFixed(
              alertThresholds[RANGES_CODES.TEMPERATURE_SKIN]?.upperLimit,
              1
            ),
            lowerLimit: SafeParser.toFixed(
              alertThresholds[RANGES_CODES.TEMPERATURE_SKIN]?.lowerLimit,
              1
            ),
          }}
        />
      </Grid>
      <Grid display='flex' flex={1} flexDirection='column' justifyContent='space-between' gap={8}>
        <FallDetector
          state={fallState}
          alertPriority={vitalsAlertSeverities[METRIC_INTERNAL_CODES.FALLS]}
          isLoading={
            isLoading ||
            (sensorsConnected[METRIC_INTERNAL_CODES.FALLS] &&
              metrics[METRIC_INTERNAL_CODES.FALLS]?.value === undefined)
          }
        />
        <BodyPosition
          position={(metrics[METRIC_INTERNAL_CODES.POSITION]?.value as POSITION_TYPES) || null}
          angle={SafeParser.toFixed(metrics[METRIC_INTERNAL_CODES.BODY_ANGLE]?.value, 0)}
          alertPriority={vitalsAlertSeverities[METRIC_INTERNAL_CODES.POSITION]}
          hoursInCurrentPosition={hoursInCurrentPosition}
          minutesInCurrentPosition={minutesInCurrentPosition}
          isConnected={sensorsConnected[METRIC_INTERNAL_CODES.POSITION]}
          isLoading={
            isLoading ||
            (sensorsConnected[METRIC_INTERNAL_CODES.POSITION] &&
              metrics[METRIC_INTERNAL_CODES.POSITION]?.value === undefined)
          }
          hasTechnicalAlert={technicalAlerts.BODY_POSITION}
          alertConditionEnabled={
            alertThresholds[RANGES_CODES.POSITION_DURATION]?.alertConditionEnabled || false
          }
        />
      </Grid>
    </Grid>
  );
};

export default VitalMetricsPanel;
