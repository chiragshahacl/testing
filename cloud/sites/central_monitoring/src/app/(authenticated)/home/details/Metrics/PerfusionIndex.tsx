import Loading from '@/app/loading';
import { ERROR_VALUE, SPO_TEXT_COLOR } from '@/constants';
import { vitalsNumberStyle } from '@/styles/styles';
import { PerfusionIndexUnit } from '@/types/metrics';
import { openSansFont } from '@/utils/fonts';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { get } from 'lodash';
import { useEffect, useState } from 'react';

type PerfusionIndexProps = {
  isLoading: boolean;
  isConnected: boolean;
  unit: PerfusionIndexUnit;
  value: string | number;
  isError: boolean;
};

const PerfusionIndex = ({
  isConnected,
  isLoading,
  unit = '%',
  isError,
  value,
}: PerfusionIndexProps) => {
  const [displayedValue, setDisplayedValue] = useState<string | number>('');

  useEffect(() => {
    if (isError && isConnected) setDisplayedValue(ERROR_VALUE);
  }, [isError, isConnected]);

  useEffect(() => {
    if (!isError && value && isConnected) setDisplayedValue(value);
  }, [isError, value, isConnected]);

  return (
    <Grid
      flexDirection='row'
      justifyContent='space-between'
      gap={8}
      className='metricCardBottomValue'
    >
      <Typography
        variant='h4'
        sx={{
          color: (theme) => get(theme.palette, SPO_TEXT_COLOR, '#57C4E8'),
        }}
      >
        PI ({unit})
      </Typography>
      {isConnected ? (
        !displayedValue && isLoading ? (
          <Grid data-testid='loading-pi' width={32}>
            <Loading height={32} size={32} thickness={2.5} />
          </Grid>
        ) : (
          <Grid
            data-testid={`pi-value-${isError ? ERROR_VALUE : value}`}
            className={openSansFont.className}
            sx={{
              ...vitalsNumberStyle,
              fontSize: 50,
              lineHeight: '68px',
              minHeight: 68,
              color: (theme) => get(theme.palette, SPO_TEXT_COLOR, '#57C4E8'),
              marginTop: '-3px',
            }}
          >
            {displayedValue}
          </Grid>
        )
      ) : null}
    </Grid>
  );
};

export default PerfusionIndex;
