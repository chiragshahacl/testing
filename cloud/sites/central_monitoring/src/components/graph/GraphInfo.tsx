import { BedType } from '@/types/bed';
import { METRIC_INTERNAL_CODES } from '@/utils/metricCodes';
import Typography from '@mui/material/Typography';
import { SHOW_TEXT } from './GraphCard';

interface GraphInfoProps {
  data: BedType;
  metric?: METRIC_INTERNAL_CODES;
  showText: SHOW_TEXT;
}

const GraphInfo = ({ data, metric, showText }: GraphInfoProps) => {
  const patientFirstName = data?.patient?.patientFirstName;
  const patientLastName = data?.patient?.patientLastName || '-';

  const getDisplayMetricName = () => {
    switch (metric) {
      case METRIC_INTERNAL_CODES.ECG:
        return 'ECG';
      case METRIC_INTERNAL_CODES.PLETH:
        return 'PLETH';
      case METRIC_INTERNAL_CODES.RR:
        return 'RR';
      default:
        return '';
    }
  };

  return (
    <>
      {showText !== SHOW_TEXT.METRIC_NAME && (
        <>
          <Typography variant='body2'>Bed ID {data.bedNo}</Typography>
          <Typography variant='caption'>{`${patientLastName}${
            patientFirstName ? `, ${patientFirstName[0]}.` : ''
          }`}</Typography>
        </>
      )}
      {showText !== SHOW_TEXT.BED_INFO && (
        <Typography
          variant='h4'
          sx={{
            color: 'vitals.green',
            position: 'absolute',
            top: 52,
            zIndex: 1,
            backgroundColor: '#0D151C',
            pr: '3px',
          }}
        >
          {getDisplayMetricName()}
        </Typography>
      )}
    </>
  );
};

export default GraphInfo;
