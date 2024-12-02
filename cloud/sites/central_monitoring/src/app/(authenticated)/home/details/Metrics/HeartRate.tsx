import Loading from '@/app/loading';
import { ERROR_VALUE, HR_TEXT_COLOR } from '@/constants';
import { ThresholdText } from '@/styles/StyledComponents';
import { vitalsNumberStyle } from '@/styles/styles';
import { HeartRateUnit } from '@/types/metrics';
import { DisplayVitalsRange } from '@/types/patientMonitor';
import { getAlertClass } from '@/utils/alertUtils';
import { openSansFont } from '@/utils/fonts';
import { ALERT_PRIORITY } from '@/utils/metricCodes';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { Theme, useTheme } from '@mui/material/styles';
import { get } from 'lodash';
import { useEffect, useState } from 'react';

type HeartRateProps = {
  alertPriority?: ALERT_PRIORITY;
  unit: HeartRateUnit;
  threshold?: DisplayVitalsRange;
  isConnected: boolean;
  isLoading: boolean;
  isError: boolean;
  value?: number | string;
};

const HeartRate = ({
  alertPriority,
  unit = 'bpm',
  threshold,
  isConnected,
  isLoading,
  isError,
  value,
}: HeartRateProps) => {
  const theme = useTheme();
  const [displayedValue, setDisplayedValue] = useState<string | number>('');

  useEffect(() => {
    if (isError && isConnected) setDisplayedValue(ERROR_VALUE);
  }, [isError, isConnected]);

  useEffect(() => {
    if (!isError && value && isConnected) setDisplayedValue(value);
  }, [isError, value, isConnected]);

  return (
    <Grid
      flex={1}
      flexDirection='column'
      data-testid='hr-metric-card'
      className={`
        metricCard 
        ${getAlertClass(alertPriority)}
        `}
    >
      <Typography
        variant='h4'
        sx={{
          color: (theme: Theme) =>
            alertPriority
              ? theme.palette.common.black
              : get(theme.palette, HR_TEXT_COLOR, '#00C868'),
        }}
      >
        HR ({unit})
      </Typography>
      <Grid display='flex' flexDirection='row' justifyContent='space-between' alignItems='flex-end'>
        <Grid>
          <ThresholdText
            color={
              alertPriority
                ? theme.palette.common.black
                : get(theme.palette, HR_TEXT_COLOR, '#00C868')
            }
          >
            {threshold?.upperLimit}
          </ThresholdText>
          <ThresholdText
            color={
              alertPriority
                ? theme.palette.common.black
                : get(theme.palette, HR_TEXT_COLOR, '#00C868')
            }
          >
            {threshold?.lowerLimit}
          </ThresholdText>
        </Grid>
        {isConnected ? (
          !displayedValue && isLoading ? (
            <Grid
              data-testid='loading-hr'
              display='flex'
              alignSelf='flex-end'
              alignItems='flex-end'
            >
              <Loading height={64} />
            </Grid>
          ) : (
            <Grid
              data-testid={`hr-value-${isError ? ERROR_VALUE : value === undefined ? '' : value}`}
              className={openSansFont.className}
              sx={{
                ...vitalsNumberStyle,
                fontSize: 90,
                lineHeight: '90px',
                color: (theme) =>
                  alertPriority
                    ? theme.palette.common.black
                    : get(theme.palette, HR_TEXT_COLOR, '#00C868'),
              }}
            >
              {displayedValue}
            </Grid>
          )
        ) : null}
      </Grid>
    </Grid>
  );
};

export default HeartRate;
