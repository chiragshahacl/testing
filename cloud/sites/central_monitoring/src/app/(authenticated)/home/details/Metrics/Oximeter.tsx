import Loading from '@/app/loading';
import { ERROR_VALUE, SPO_TEXT_COLOR } from '@/constants';
import { ThresholdText } from '@/styles/StyledComponents';
import { vitalsNumberStyle } from '@/styles/styles';
import { OximeterUnit } from '@/types/metrics';
import { DisplayVitalsRange } from '@/types/patientMonitor';
import { getAlertClass } from '@/utils/alertUtils';
import { openSansFont } from '@/utils/fonts';
import { ALERT_PRIORITY } from '@/utils/metricCodes';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { Theme, useTheme } from '@mui/material/styles';
import { get } from 'lodash';
import { useEffect, useState } from 'react';

type OximeterProps = {
  alertPriority?: ALERT_PRIORITY;
  unit: OximeterUnit;
  threshold?: DisplayVitalsRange;
  isConnected: boolean;
  isLoading: boolean;
  isError: boolean;
  value?: number | string;
};
const Oximeter = ({
  alertPriority,
  unit = '%',
  threshold,
  isConnected,
  isLoading,
  isError,
  value,
}: OximeterProps) => {
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
      flexDirection='column'
      data-testid='spo-metric-field'
      className={`
        metricCardTopValue 
        ${alertPriority ? 'metricCardWithAlert' : ''}
        ${getAlertClass(alertPriority)}
        `}
    >
      <Typography
        variant='h4'
        sx={{
          color: (theme: Theme) =>
            alertPriority
              ? theme.palette.common.black
              : get(theme.palette, SPO_TEXT_COLOR, '#57C4E8'),
        }}
      >
        SPO2 ({unit})
      </Typography>
      <Grid display='flex' flexDirection='row' justifyContent='space-between' alignItems='flex-end'>
        <Grid>
          <ThresholdText
            color={
              alertPriority
                ? theme.palette.common.black
                : get(theme.palette, SPO_TEXT_COLOR, '#57C4E8')
            }
          >
            {threshold?.upperLimit}
          </ThresholdText>
          <ThresholdText
            color={
              alertPriority
                ? theme.palette.common.black
                : get(theme.palette, SPO_TEXT_COLOR, '#57C4E8')
            }
          >
            {threshold?.lowerLimit}
          </ThresholdText>
        </Grid>
        {isConnected ? (
          !displayedValue && isLoading ? (
            <Grid
              data-testid='loading-spo2'
              display='flex'
              alignSelf='flex-end'
              alignItems='flex-end'
            >
              <Loading height={32} size={32} thickness={2.5} />
            </Grid>
          ) : (
            <Grid
              data-testid={`spo-value-${isError ? ERROR_VALUE : value === undefined ? '' : value}`}
              className={openSansFont.className}
              sx={{
                ...vitalsNumberStyle,
                fontSize: 50,
                lineHeight: '68px',
                marginTop: '-3px',
                color: (theme) =>
                  alertPriority
                    ? theme.palette.common.black
                    : get(theme.palette, SPO_TEXT_COLOR, '#57C4E8'),
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

export default Oximeter;
