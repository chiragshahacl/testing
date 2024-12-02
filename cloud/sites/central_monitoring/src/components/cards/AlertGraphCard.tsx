import { getAlertColor } from '@/utils/alertUtils';
import { ALERT_PRIORITY } from '@/utils/metricCodes';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { CSSObject, alpha } from '@mui/material/styles';

interface AlertGraphCardProps {
  priority?: ALERT_PRIORITY;
  alertMessage?: string;
  secondLineAlertMessage?: string;
  height: string | number;
  width?: string;
  textBg?: string;
  styles?: CSSObject;
}

const AlertGraphCard = ({
  priority,
  alertMessage,
  secondLineAlertMessage,
  height,
  width = 'fit-content',
  textBg = alpha('rgb(1,1,1)', 0.6),
  styles = {},
}: AlertGraphCardProps) => {
  return (
    <Grid
      display='flex'
      justifyContent='center'
      alignItems='center'
      data-testid='alert-graph-card'
      sx={{
        flexDirection: 'column',
        position: 'relative',
        borderRadius: 8,
        zIndex: 1,
        gap: 3,
        backgroundColor: getAlertColor(priority)
          ? // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
            alpha(getAlertColor(priority)!, 0.25) // color can never be undefined regardless of the return type because of the previous check
          : 'transparent',
        height,
        ...styles,
      }}
    >
      <Typography
        variant='overline'
        textAlign='center'
        textTransform='uppercase'
        sx={{
          width,
          lineHeight: 0,
          minWidth: '50%',
          padding: (theme) => theme.spacing(10, 15),
          backgroundColor: textBg,
          color: (theme) =>
            getAlertColor(priority) ? getAlertColor(priority) : theme.palette.grey[200],
        }}
      >
        {alertMessage}
      </Typography>
      {secondLineAlertMessage && (
        <Typography
          variant='overline'
          textAlign='center'
          textTransform='uppercase'
          sx={{
            width,
            lineHeight: 0,
            minWidth: '50%',
            padding: (theme) => theme.spacing(10, 15),
            backgroundColor: textBg,
            color: (theme) =>
              getAlertColor(priority) ? getAlertColor(priority) : theme.palette.grey[200],
          }}
        >
          {secondLineAlertMessage}
        </Typography>
      )}
    </Grid>
  );
};

export default AlertGraphCard;
