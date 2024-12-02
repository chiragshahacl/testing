import Loading from '@/app/loading';
import { DISPLAY_DIRECTION, ERROR_VALUE, disabledColor } from '@/constants';
import { ThresholdText } from '@/styles/StyledComponents';
import { Measurement } from '@/types/metrics';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { Theme, useTheme } from '@mui/material/styles';
import { get } from 'lodash';
import { useEffect, useState } from 'react';

type MeasurementProps = {
  measurement: Measurement;
  hasAlert: boolean;
  hasTechnicalAlert: boolean;
  isLoading: boolean;
  isError: boolean;
  isConnected: boolean;
  testid: string;
  showDisconnectedData: boolean;
  direction?: DISPLAY_DIRECTION;
};

const MeasurementReading = ({
  measurement,
  hasAlert,
  hasTechnicalAlert,
  isLoading,
  isError,
  isConnected,
  testid,
  showDisconnectedData,
  direction = DISPLAY_DIRECTION.LTR,
}: MeasurementProps) => {
  const theme = useTheme();
  const [displayedValue, setDisplayedValue] = useState<string | number>('');

  useEffect(() => {
    if (isError) setDisplayedValue(ERROR_VALUE);
  }, [isError]);

  useEffect(() => {
    if (!isError && measurement.value) setDisplayedValue(measurement.value);
  }, [isError, measurement]);

  return (
    <Grid
      display='flex'
      flex={1}
      width='100%'
      flexDirection={direction === DISPLAY_DIRECTION.LTR ? 'row' : 'row-reverse'}
      alignSelf='flex-end'
      justifyContent={
        measurement.upperLimit && measurement.lowerLimit ? 'space-between' : 'flex-end'
      }
    >
      {measurement.upperLimit && measurement.lowerLimit && (
        <Grid
          sx={{
            lineHeight: '15px',
            margin: (theme: Theme) =>
              direction === DISPLAY_DIRECTION.LTR
                ? `${theme.spacing(0, 9, 5, 0)}`
                : `${theme.spacing(0, 0, 5, 9)}`,
            whiteSpace: 'nowrap',
          }}
        >
          <ThresholdText
            color={
              !isConnected && !showDisconnectedData
                ? disabledColor
                : hasTechnicalAlert
                ? get(theme.palette, 'alert.low')
                : hasAlert
                ? theme.palette.common.black
                : theme.palette.divider
            }
          >
            {measurement.upperLimit}
          </ThresholdText>
          <ThresholdText
            color={
              !isConnected && !showDisconnectedData
                ? disabledColor
                : hasTechnicalAlert
                ? get(theme.palette, 'alert.low')
                : hasAlert
                ? theme.palette.common.black
                : theme.palette.divider
            }
          >
            {measurement.lowerLimit}
          </ThresholdText>
        </Grid>
      )}
      {isConnected || showDisconnectedData ? (
        !displayedValue &&
        !showDisconnectedData &&
        (isLoading || measurement.value == undefined) ? (
          <Grid display='flex' justifyContent='flex-end'>
            <Loading height='100%' size={32} thickness={2.5} />
          </Grid>
        ) : (
          <Typography
            data-testid={`metric-value-${testid}`}
            variant='metricNumberStyles'
            sx={{
              color:
                !isConnected && !showDisconnectedData
                  ? disabledColor
                  : hasTechnicalAlert
                  ? get(theme.palette, 'alert.low')
                  : hasAlert
                  ? theme.palette.common.black
                  : theme.palette.divider,
              whiteSpace: 'nowrap',
            }}
          >
            {displayedValue}
          </Typography>
        )
      ) : null}
    </Grid>
  );
};

interface MeasurementIndicatorProps {
  hasAlert?: boolean;
  hasTechnicalAlert?: boolean;
  isLoading?: boolean;
  isError?: boolean;
  isConnected?: boolean;
  measurement: Measurement;
  testid: string;
  showDisconnectedData?: boolean;
}

const MeasurementIndicator = ({
  hasAlert = false,
  hasTechnicalAlert = false,
  isLoading = false,
  isError = false,
  isConnected = false,
  measurement,
  testid,
  showDisconnectedData = false,
}: MeasurementIndicatorProps) => (
  <Grid
    data-testid={testid}
    display='flex'
    width='100%'
    flexDirection='row'
    alignSelf='flex-end'
    justifyContent='space-between'
  >
    <MeasurementReading
      measurement={measurement}
      hasAlert={hasAlert}
      hasTechnicalAlert={hasTechnicalAlert}
      isLoading={isLoading}
      isError={isError}
      isConnected={isConnected}
      showDisconnectedData={showDisconnectedData}
      testid={testid}
    />
  </Grid>
);

export default MeasurementIndicator;
export { MeasurementReading };
