import MeasurementIndicator from '@/app/(authenticated)/home/details/Metrics/MeasurementIndicator';
import VitalInfoComponent from '@/app/(authenticated)/home/details/VitalInfoComponent';
import { Measurement, TemperatureUnit } from '@/types/metrics';
import { getAlertClass } from '@/utils/alertUtils';
import { ALERT_PRIORITY } from '@/utils/metricCodes';
import Grid from '@mui/material/Grid';

type ChestTemperatureProps = {
  alertPriority?: ALERT_PRIORITY;
  unit: TemperatureUnit;
  isLoading: boolean;
  isConnected: boolean;
  measurement: Measurement;
  isError: boolean;
};

const ChestTemperature = ({
  alertPriority,
  unit = '°F',
  isLoading,
  isConnected,
  measurement,
  isError,
}: ChestTemperatureProps) => {
  return (
    <Grid
      data-testid={'chest-temp-metric-card'}
      flex={1}
      flexDirection='column'
      className={`
    metricCard 
    ${getAlertClass(alertPriority)}
    `}
      sx={{
        ...(!alertPriority && {
          borderRadius: '8px 0px 0px 8px',
          marginRight: '-18px',
          paddingRight: 28,
        }),
      }}
    >
      <VitalInfoComponent
        title={`SKIN TEMP (${unit})`}
        subtitle='CHEST TEMP'
        hasAlert={!!alertPriority}
      />
      <MeasurementIndicator
        testid={`chest-temp-${measurement?.value === undefined ? '' : measurement.value}`}
        hasAlert={!!alertPriority}
        isLoading={isLoading}
        isConnected={isConnected}
        measurement={measurement}
        isError={isError}
      />
    </Grid>
  );
};

export default ChestTemperature;
