import MeasurementIndicator from '@/app/(authenticated)/home/details/Metrics/MeasurementIndicator';
import VitalInfoComponent from '@/app/(authenticated)/home/details/VitalInfoComponent';
import { measurementErrors } from '@/constants';
import { Measurement, PulseRateUnit } from '@/types/metrics';
import { timeFromNow } from '@/utils/moment';
import Grid from '@mui/material/Grid';

type PulseRateProps = {
  unit: PulseRateUnit;
  isConnected: boolean;
  isLoading: boolean;
  timestamp?: string;
  measurement: Measurement;
  measureFailed: boolean;
  isError: boolean;
};

const PulseRate = ({
  unit = 'bpm',
  isConnected,
  isLoading,
  timestamp,
  measurement,
  measureFailed,
  isError,
}: PulseRateProps) => {
  return (
    <Grid
      data-testid={'pulse-metric-card'}
      flex={1}
      flexDirection='column'
      className='metricCard'
      sx={{
        borderRadius: '8px 0px 0px 8px',
        marginRight: '-18px',
        paddingRight: 28,
      }}
    >
      <VitalInfoComponent
        title={`PULSE (${unit})`}
        hasTechnicalAlert={measureFailed}
        subtitle={
          measureFailed ? measurementErrors.measureFailed : timestamp && timeFromNow(timestamp)
        }
      />
      <MeasurementIndicator
        testid={`pulse-${measurement.value === undefined ? '' : measurement.value}`}
        measurement={measurement}
        hasTechnicalAlert={measureFailed}
        isLoading={isLoading}
        isConnected={isConnected}
        isError={isError}
        showDisconnectedData
      />
    </Grid>
  );
};

export default PulseRate;
