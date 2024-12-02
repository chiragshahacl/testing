import { DEVICE_ALERT_CODES } from '@/utils/metricCodes';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';

interface NoDataBedProps {
  bedNo: string;
  onClick?: () => void;
}

const NoDataBed = ({ bedNo, onClick = () => undefined }: NoDataBedProps) => {
  return (
    <Grid
      className='column'
      sx={{
        padding: (theme) => theme.spacing(8, 12),
        backgroundColor: 'primary.dark',
        borderRadius: 16,
        width: '49%',
        cursor: 'pointer',
      }}
      onClick={onClick}
    >
      <Grid
        className='column'
        position='relative'
        justifyContent='center'
        display='flex'
        sx={{
          padding: (theme) => theme.spacing(4, 12),
          backgroundColor: 'primary.dark',
          borderRadius: 8,
          height: '100%',
        }}
      >
        <Grid
          position='absolute'
          display='flex'
          flexDirection='column'
          justifyContent='flex-start'
          top={0}
          left={0}
        >
          <Grid>Bed ID {bedNo}</Grid>
          <Grid>-</Grid>
        </Grid>
        <Typography variant='overline' textAlign='center' textTransform='uppercase'>
          {DEVICE_ALERT_CODES.MONITOR_NOT_AVAILABLE_ALERT.waveformMessage}
        </Typography>
      </Grid>
    </Grid>
  );
};

export default NoDataBed;
