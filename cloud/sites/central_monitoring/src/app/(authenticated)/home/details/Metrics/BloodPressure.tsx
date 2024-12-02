import VitalInfoComponent from '@/app/(authenticated)/home/details/VitalInfoComponent';
import { BloodPressureUnit, Measurement } from '@/types/metrics';
import { getAlertClass } from '@/utils/alertUtils';
import { ALERT_PRIORITY } from '@/utils/metricCodes';
import { timeFromNow } from '@/utils/moment';
import Grid from '@mui/material/Grid';
import RangeIndicator from './RangeIndicator';
import { measurementErrors } from '@/constants';
import MapIndicator from './MapIndicator';

type BloodPressureProps = {
  alertPriority?: ALERT_PRIORITY;
  unit: BloodPressureUnit;
  isConnected: boolean;
  timestamp?: string;
  isLoading: boolean;
  measureFailed: boolean;
  diastolicMeasurement: Measurement;
  systolicMeasurement: Measurement;
  mapMeasurement: number | string | undefined;
  diastolicError: boolean;
  systolicError: boolean;
  mapError: boolean;
};

const BloodPressure = ({
  alertPriority,
  diastolicMeasurement,
  systolicMeasurement,
  mapMeasurement,
  isConnected,
  timestamp,
  systolicError,
  diastolicError,
  mapError,
  isLoading,
  measureFailed,
  unit = 'mmHg',
}: BloodPressureProps) => {
  return (
    <Grid
      data-testid={'bp-metric-card'}
      flex={1}
      flexDirection='column'
      className={`
    metricCard 
    ${getAlertClass(alertPriority)}
    `}
      sx={{
        ...(!alertPriority && {
          borderRadius: '0px 8px 8px 0px',
          marginLeft: '-18px',
          paddingLeft: 18,
        }),
      }}
    >
      <VitalInfoComponent
        title={`NIBP (${unit})`}
        subtitle={
          measureFailed ? measurementErrors.measureFailed : timestamp && timeFromNow(timestamp)
        }
        hasTechnicalAlert={measureFailed}
        hasAlert={!!alertPriority}
      />
      <RangeIndicator
        leftMeasurement={systolicMeasurement}
        leftTestid={`nibp-sys-${
          systolicMeasurement.value === undefined ? '' : systolicMeasurement.value
        }`}
        rightMeasurement={diastolicMeasurement}
        rightTestid={`nibp-dia-${
          diastolicMeasurement.value === undefined ? '' : diastolicMeasurement.value
        }`}
        leftError={systolicError}
        rightError={diastolicError}
        isLoading={isLoading}
        isConnected={isConnected}
        hasTechnicalAlert={measureFailed}
        hasAlert={!!alertPriority}
        showDisconnectedData
      />
      <MapIndicator
        hasAlert={!!alertPriority}
        hasTechnicalAlert={measureFailed}
        hasError={mapError}
        measurement={mapMeasurement}
        isLoading={isLoading}
      />
    </Grid>
  );
};

export default BloodPressure;
