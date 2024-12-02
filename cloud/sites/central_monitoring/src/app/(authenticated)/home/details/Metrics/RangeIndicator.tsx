import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { Theme } from '@mui/material/styles';
import { Measurement } from '../../../../../types/metrics';
import { MeasurementReading } from './MeasurementIndicator';
import { get } from 'lodash';
import { DISPLAY_DIRECTION } from '@/constants';

type RangeIndicatorProps = {
  leftTestid: string;
  rightTestid: string;
  leftMeasurement: Measurement;
  rightMeasurement: Measurement;
  leftError: boolean;
  rightError: boolean;
  isLoading: boolean;
  isConnected: boolean;
  hasAlert: boolean;
  hasTechnicalAlert?: boolean;
  showDisconnectedData?: boolean;
};

const RangeIndicator = ({
  hasAlert,
  hasTechnicalAlert = false,
  leftMeasurement,
  rightMeasurement,
  leftError,
  rightError,
  isLoading,
  isConnected,
  leftTestid,
  rightTestid,
  showDisconnectedData = false,
}: RangeIndicatorProps) => {
  return (
    <Grid
      display='flex'
      width='100%'
      flexDirection='row'
      alignSelf='flex-end'
      justifyContent='space-between'
    >
      <MeasurementReading
        testid={leftTestid}
        hasTechnicalAlert={hasTechnicalAlert}
        hasAlert={hasAlert}
        isLoading={isLoading}
        measurement={leftMeasurement}
        isError={leftError}
        isConnected={isConnected}
        showDisconnectedData={showDisconnectedData}
      />
      <Typography
        variant='metricNumberStyles'
        sx={{
          flex: 1,
          justifyContent: 'center',
          margin: (theme: Theme) => theme.spacing(0, 8),
          color: (theme: Theme) =>
            hasTechnicalAlert
              ? get(theme.palette, 'alert.low')
              : hasAlert
              ? theme.palette.common.black
              : theme.palette.divider,
        }}
      >
        /
      </Typography>
      <MeasurementReading
        testid={rightTestid}
        hasTechnicalAlert={hasTechnicalAlert}
        hasAlert={hasAlert}
        isLoading={isLoading}
        measurement={rightMeasurement}
        isError={rightError}
        isConnected={isConnected}
        showDisconnectedData={showDisconnectedData}
        direction={DISPLAY_DIRECTION.RTL}
      />
    </Grid>
  );
};

export default RangeIndicator;
