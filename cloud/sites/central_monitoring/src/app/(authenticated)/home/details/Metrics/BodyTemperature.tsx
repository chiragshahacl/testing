import MeasurementIndicator from '@/app/(authenticated)/home/details/Metrics/MeasurementIndicator';
import VitalInfoComponent from '@/app/(authenticated)/home/details/VitalInfoComponent';
import { Measurement, TemperatureUnit } from '@/types/metrics';
import { getAlertClass } from '@/utils/alertUtils';
import { ALERT_PRIORITY } from '@/utils/metricCodes';
import { timeFromNow } from '@/utils/moment';
import Grid from '@mui/material/Grid';

type BodyTemperatureProps = {
  unit: TemperatureUnit;
  isLoading: boolean;
  isConnected: boolean;
  timestamp: string;
  measurement: Measurement;
  alertPriority?: ALERT_PRIORITY;
  isError: boolean;
};
const BodyTemperature = ({
  unit = '°F',
  isLoading,
  isConnected,
  timestamp,
  measurement,
  alertPriority,
  isError,
}: BodyTemperatureProps) => {
  return (
    <Grid
      data-testid={'body-temp-metric-card'}
      flex={1}
      flexDirection='column'
      className={`
        metricCard 
        ${getAlertClass(alertPriority)}
        `}
    >
      <VitalInfoComponent
        title={`BODY TEMP (${unit})`}
        subtitle={timestamp && timeFromNow(timestamp)}
        hasAlert={!!alertPriority}
      />
      <MeasurementIndicator
        testid={`body-temp-${measurement?.value === undefined ? '' : measurement.value}`}
        hasAlert={!!alertPriority}
        isLoading={isLoading}
        isConnected={isConnected}
        measurement={measurement}
        isError={isError}
        showDisconnectedData
      />
    </Grid>
  );
};

export default BodyTemperature;
