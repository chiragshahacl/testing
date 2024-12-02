import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { Theme } from '@mui/material/styles';
import { get } from 'lodash';
import { ThresholdText } from '@/styles/StyledComponents';
import Loading from '@/app/loading';
import { ERROR_VALUE } from '@/constants';

type MapIndicatorProps = {
  measurement: number | string | undefined;
  isLoading: boolean;
  hasAlert: boolean;
  hasTechnicalAlert?: boolean;
  hasError: boolean;
};

const MapIndicator = ({
  hasAlert,
  hasTechnicalAlert = false,
  measurement,
  hasError,
  isLoading,
}: MapIndicatorProps) => {
  return (
    <Grid
      display='flex'
      flexDirection='row'
      alignSelf='flex-end'
      justifyContent='space-between'
      marginRight={24}
    >
      <ThresholdText
        sx={{
          color: (theme: Theme) =>
            hasTechnicalAlert
              ? get(theme.palette, 'alert.low')
              : hasAlert
              ? theme.palette.common.black
              : theme.palette.divider,
        }}
      >
        MAP
      </ThresholdText>
      <Typography
        variant='metricNumberStyles'
        sx={{
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
        {'('}
      </Typography>
      <Grid minWidth={32}>
        {isLoading ? (
          <Grid display='flex' justifyContent='flex-end'>
            <Loading height='100%' size={32} thickness={2.5} />
          </Grid>
        ) : (
          <Typography
            data-testid={`metric-value-nibp-map-${String(
              hasError || hasTechnicalAlert ? ERROR_VALUE : measurement
            )}`}
            variant='metricNumberStyles'
            sx={{
              color: (theme: Theme) =>
                hasTechnicalAlert
                  ? get(theme.palette, 'alert.low')
                  : hasAlert
                  ? theme.palette.common.black
                  : theme.palette.divider,
              whiteSpace: 'nowrap',
            }}
          >
            {hasError || hasTechnicalAlert ? ERROR_VALUE : measurement}
          </Typography>
        )}
      </Grid>
      <Typography
        variant='metricNumberStyles'
        sx={{
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
        {')'}
      </Typography>
    </Grid>
  );
};

export default MapIndicator;
