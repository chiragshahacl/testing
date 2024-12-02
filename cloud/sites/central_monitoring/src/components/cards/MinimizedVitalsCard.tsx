import { DISPLAY_ERRORS, ERROR_VALUE } from '@/constants';
import { TECHNICAL_ALERT_TYPE } from '@/utils/alertUtils';
import { SafeParser } from '@/utils/safeParser';
import Grid from '@mui/material/Grid';
import { get } from 'lodash';
import ThreeDigitCard from './ThreeDigitCard';
import theme from '@/theme/theme';
import Typography from '@mui/material/Typography';
import { EncounterStatus } from '@/types/encounters';
import { useMemo } from 'react';

interface MinimizedVitalsCardProps {
  isLoading: boolean;
  encounterStatus?: EncounterStatus;
  isPatientMonitorAvailable: boolean;
  technicalAlerts: Record<TECHNICAL_ALERT_TYPE, boolean>;
  metricInfo: Record<
    string,
    {
      limits: {
        upperLimit?: number | string;
        lowerLimit?: number | string;
      };
      value?: number | string | null;
      isSensorConnected: boolean;
      hasAlert: boolean;
    }
  >;
}

const MinimizedVitalsCard = ({
  isLoading,
  isPatientMonitorAvailable,
  encounterStatus,
  technicalAlerts,
  metricInfo,
}: MinimizedVitalsCardProps) => {
  const encounterStatusMessage = useMemo(() => {
    if (encounterStatus === EncounterStatus.CANCELLED) return 'ADMISSION REJECTED';
    else if (encounterStatus === EncounterStatus.PLANNED) return 'PENDING CONFIRMATION';
    return 'SELECT TO ADMIT PATIENT';
  }, [encounterStatus]);

  if (isLoading || !isPatientMonitorAvailable) {
    return (
      <Grid display='flex' flex={1} alignItems='center'>
        <Typography
          variant='overline'
          textAlign='center'
          textTransform='uppercase'
          sx={{
            width: '100%',
            height: '50%',
            padding: (theme) => theme.spacing(10, 15),
            backgroundColor: 'primary.dark',
            color: (theme) => theme.palette.grey[200],
          }}
        >
          {(isLoading && 'LOADING...') ||
            (!isPatientMonitorAvailable && DISPLAY_ERRORS.NOT_AVAILABLE)}
        </Typography>
      </Grid>
    );
  }

  if (encounterStatus !== EncounterStatus.IN_PROGRESS) {
    return (
      <Grid display='flex' flex={1} alignItems='center'>
        <Typography
          variant='h3'
          textAlign='center'
          textTransform='uppercase'
          sx={{
            width: '100%',
            height: '50%',
            padding: (theme) => theme.spacing(10, 0),
            color: (theme) => theme.palette.grey[200],
          }}
        >
          {encounterStatusMessage}
        </Typography>
      </Grid>
    );
  }

  return (
    <Grid display='flex' gap={24} mb={4.6}>
      {['HR', 'SPO'].map((metric) => (
        <ThreeDigitCard
          key={metric}
          title={metric === 'SPO' ? 'SPO2' : metric}
          firstSmall={metricInfo[metric].limits.upperLimit}
          secondSmall={metricInfo[metric].limits.lowerLimit}
          color={
            metric === 'SPO'
              ? get(theme.palette, 'vitals.blue')
              : get(theme.palette, 'vitals.green')
          }
          bigData={
            !metricInfo[metric].isSensorConnected
              ? ''
              : get(technicalAlerts, get(TECHNICAL_ALERT_TYPE, metric))
              ? ERROR_VALUE
              : metricInfo[metric]?.value
              ? SafeParser.toFixed(metricInfo[metric].value)
              : metricInfo[metric]?.value === null
              ? ERROR_VALUE
              : undefined
          }
          hasAlert={metricInfo[metric].hasAlert}
        />
      ))}
    </Grid>
  );
};

export default MinimizedVitalsCard;
