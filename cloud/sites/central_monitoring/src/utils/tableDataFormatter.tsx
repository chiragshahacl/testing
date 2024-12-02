import PhysiologicalIcon from '@/components/icons/alarm/PhysiologicalIcon';
import TechnicalIcon from '@/components/icons/alarm/TechnicalIcon';
import { AlarmRecord } from '@/types/alerts';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { openSansFont } from './fonts';
import { ALERT_PRIORITY_LABEL, ALERT_PRIORITY, ALERT_TYPES } from './metricCodes';
import moment from 'moment';
import { getCachedRuntimeConfig } from './runtime';
import { styled } from '@mui/material/styles';

const FieldText = styled(Typography)(() => ({
  lineHeight: '21.79px',
}));

const getAlarmTypeIcon = (type: string): React.ReactElement => {
  if (type === ALERT_TYPES.VITALS) {
    return <PhysiologicalIcon />;
  } else if (type === ALERT_TYPES.DEVICE) {
    return <TechnicalIcon />;
  } else {
    return <></>;
  }
};

const getAlarmTypeText = (type: string): string => {
  if (type === ALERT_TYPES.VITALS) {
    return 'Physiological';
  } else if (type === ALERT_TYPES.DEVICE) {
    return 'Technical';
  } else {
    return '';
  }
};

const HOSPITAL_TIMEZONE = getCachedRuntimeConfig().HOSPITAL_TZ ?? 'UTC';

export const formatCellData = (dataKey: keyof AlarmRecord, value: string): React.ReactElement => {
  switch (dataKey) {
    case 'type':
      return (
        <Grid display='flex' flexDirection='row' gap={8}>
          {getAlarmTypeIcon(value)}
          <FieldText className={openSansFont.className} variant='caption'>
            {getAlarmTypeText(value)}
          </FieldText>
        </Grid>
      );
    case 'date':
      return (
        <FieldText className={openSansFont.className} variant='caption'>
          {moment.tz(value, 'UTC').tz(HOSPITAL_TIMEZONE).format('YYYY-MM-DD')}
        </FieldText>
      );
    case 'priority':
      return (
        <FieldText className={openSansFont.className} variant='caption'>
          {ALERT_PRIORITY_LABEL[value as ALERT_PRIORITY] ?? 'Unknown'}
        </FieldText>
      );
    case 'time':
      return (
        <FieldText className={openSansFont.className} variant='caption'>
          {moment.tz(value, 'UTC').tz(HOSPITAL_TIMEZONE).format('HH:mm:ss')}
        </FieldText>
      );
    case 'duration':
      return (
        <FieldText className={openSansFont.className} variant='caption'>
          {value}
        </FieldText>
      );
    default:
      return (
        <FieldText className={openSansFont.className} variant='caption'>
          {value}
        </FieldText>
      );
  }
};
