import Loading from '@/app/loading';
import { ERROR_VALUE, RR_TEXT_COLOR } from '@/constants';
import { ThresholdText } from '@/styles/StyledComponents';
import { vitalsNumberStyle } from '@/styles/styles';
import { RespiratoryRateUnit } from '@/types/metrics';
import { DisplayVitalsRange } from '@/types/patientMonitor';
import { getAlertClass } from '@/utils/alertUtils';
import { openSansFont } from '@/utils/fonts';
import { ALERT_PRIORITY } from '@/utils/metricCodes';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { Theme, useTheme } from '@mui/material/styles';
import { get } from 'lodash';
import { useEffect, useState } from 'react';

type RespiratoryRateProps = {
  alertPriority?: ALERT_PRIORITY;
  unit?: RespiratoryRateUnit;
  isConnected: boolean;
  threshold?: DisplayVitalsRange;
  value?: number | string;
  isLoading: boolean;
  isError: boolean;
};

const RespiratoryRate = ({
  alertPriority,
  unit = 'brpm',
  isConnected,
  threshold,
  value,
  isLoading,
  isError,
}: RespiratoryRateProps) => {
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
      data-testid='rr-metric-card'
      className={`
    metricCard 
    ${getAlertClass(alertPriority)}
    `}
    >
      <Typography
        variant='h4'
        sx={{
          color: (theme: Theme) =>
            alertPriority ? theme.palette.common.black : get(theme.palette, RR_TEXT_COLOR),
        }}
      >
        RR ({unit})
      </Typography>
      <Grid display='flex' flexDirection='row' justifyContent='space-between' alignItems='flex-end'>
        <Grid>
          <ThresholdText
            color={alertPriority ? theme.palette.common.black : get(theme.palette, RR_TEXT_COLOR)}
          >
            {threshold?.upperLimit}
          </ThresholdText>
          <ThresholdText
            color={alertPriority ? theme.palette.common.black : get(theme.palette, RR_TEXT_COLOR)}
          >
            {threshold?.lowerLimit}
          </ThresholdText>
        </Grid>
        {isConnected ? (
          !displayedValue && isLoading ? (
            <Grid
              data-testid='loading-rr'
              minHeight={36}
              display='flex'
              alignSelf='flex-end'
              alignItems='flex-end'
            >
              <Loading size={30} height={30} />
            </Grid>
          ) : (
            <Grid
              data-testid={`rr-value-${isError ? ERROR_VALUE : value === undefined ? '' : value}`}
              className={openSansFont.className}
              sx={{
                ...vitalsNumberStyle,
                fontSize: 30,
                lineHeight: '30px',
                color: (theme) =>
                  alertPriority ? theme.palette.common.black : get(theme.palette, RR_TEXT_COLOR),
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

export default RespiratoryRate;
