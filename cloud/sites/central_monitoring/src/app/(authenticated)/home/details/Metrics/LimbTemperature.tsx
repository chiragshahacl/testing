import MeasurementIndicator from '@/app/(authenticated)/home/details/Metrics/MeasurementIndicator';
import VitalInfoComponent from '@/app/(authenticated)/home/details/VitalInfoComponent';
import { Measurement } from '@/types/metrics';
import { getAlertClass } from '@/utils/alertUtils';
import { ALERT_PRIORITY } from '@/utils/metricCodes';
import Grid from '@mui/material/Grid';

type LimbTemperatureProps = {
  isConnected: boolean;
  alertPriority?: ALERT_PRIORITY;
  isLoading: boolean;
  measurement: Measurement;
  isError: boolean;
};

const LimbTemperature = ({
  isConnected,
  alertPriority,
  isLoading,
  measurement,
  isError,
}: LimbTemperatureProps) => {
  return (
    <Grid
      data-testid={`limb-temp-metric-card limb-temp-sensors-${
        isConnected ? 'connected' : 'not-connected'
      }`}
      flex={1}
      flexDirection='column'
      className={`
          metricCard 
          ${isConnected ? getAlertClass(alertPriority) : ''}
          `}
      sx={{
        ...(isConnected &&
          !alertPriority && {
            borderRadius: '0px 8px 8px 0px',
            marginLeft: '-18px',
            paddingLeft: 18,
          }),
      }}
    >
      <VitalInfoComponent subtitle='LIMB TEMP' hasAlert={!!alertPriority} disabled={!isConnected} />
      <MeasurementIndicator
        testid={`limb-temp-${measurement?.value === undefined ? '' : measurement.value}`}
        hasAlert={!!alertPriority}
        isLoading={isLoading}
        isConnected={isConnected}
        measurement={measurement}
        isError={isError}
      />
    </Grid>
  );
};

export default LimbTemperature;
