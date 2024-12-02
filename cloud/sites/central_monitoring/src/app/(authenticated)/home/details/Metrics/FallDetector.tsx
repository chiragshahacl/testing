import Loading from '@/app/loading';
import FallIcon from '@/components/icons/FallIcon';
import { ERROR_VALUE } from '@/constants';
import { FallState } from '@/types/metrics';
import { getAlertClass } from '@/utils/alertUtils';
import { ALERT_PRIORITY } from '@/utils/metricCodes';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

const getTitle = (state: FallState | null): string => {
  switch (state) {
    case FallState.DETECTED:
      return 'DETECTED';
    case FallState.NOT_DETECTED:
      return 'NOT DETECTED';
    default:
      return '';
  }
};

interface FallDetectorMetricProps {
  isLoading: boolean;
  alertPriority?: ALERT_PRIORITY;
  state: FallState | null;
}

const FallDetectorMetric = ({ isLoading, state, alertPriority }: FallDetectorMetricProps) => {
  const theme = useTheme();
  return (
    <Grid
      data-testid={'fall-metric-card'}
      display='flex'
      flexDirection='row'
      justifyContent='space-between'
      className={`
        metricCard 
        ${getAlertClass(alertPriority)}
        `}
    >
      <Grid display='flex' flexDirection='row' alignItems='center'>
        <FallIcon darkIcon={!!alertPriority} />
        <Typography
          variant='h4'
          sx={{
            color: alertPriority ? theme.palette.common.black : theme.palette.divider,
            margin: (theme) => theme.spacing(0, 6, 0, 5),
          }}
        >
          FALL
        </Typography>
      </Grid>

      {isLoading ? (
        <Grid display='flex' justifyContent='flex-end'>
          <Loading height='100%' thickness={2.5} size={46} />
        </Grid>
      ) : state === FallState.UNKNOWN ? (
        <Typography
          variant='body1'
          sx={{
            textAlign: 'right',
            color: alertPriority ? theme.palette.common.black : theme.palette.divider,
            fontWeight: 600,
            lineHeight: '46px',
          }}
        >
          {ERROR_VALUE}
        </Typography>
      ) : (
        <Typography
          variant='body1'
          sx={{
            textAlign: 'right',
            color: alertPriority ? theme.palette.common.black : theme.palette.divider,
            fontWeight: 600,
          }}
        >
          {getTitle(state)}
        </Typography>
      )}
    </Grid>
  );
};

export default FallDetectorMetric;
