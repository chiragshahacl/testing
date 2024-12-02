import { ALERT_TEXT_COLOR } from '@/utils/alertUtils';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';

interface NumberBadgeProps {
  number: number;
  color?: string;
}

const NumberBadge = ({ number, color = 'white' }: NumberBadgeProps) => {
  return (
    <Grid
      style={{
        alignSelf: 'center',
        color: 'error.main',
        backgroundColor: ALERT_TEXT_COLOR,
        borderRadius: 16,
        width: 26,
        height: 26,
      }}
    >
      <Grid
        style={{
          display: 'flex',
          alignSelf: 'center',
          height: '100%',
          width: '100%',
          alignItems: 'center',
          justifyContent: 'center',
          color,
        }}
      >
        <Typography variant='caption'>{number}</Typography>
      </Grid>
    </Grid>
  );
};

export default NumberBadge;
