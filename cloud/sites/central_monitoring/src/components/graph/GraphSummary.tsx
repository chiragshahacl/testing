import { styled } from '@mui/material/styles';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { get } from 'lodash';

const ThresholdText = styled(Typography, {
  shouldForwardProp: (prop) => prop !== 'smallView',
})<{ smallView?: boolean }>(({ theme, smallView }) => ({
  fontSize: smallView ? 11 : 14,
  fontWeight: 400,
  color: get(theme.palette, 'vitals.green'),
  lineHeight: smallView ? '13px' : '16px',
}));

interface GraphSummaryProps {
  data: {
    hr: string;
    highLimit: string;
    lowLimit: string;
  };
  smallView?: boolean;
  alertColor: string;
}

const GraphSummary = ({ data, smallView = false, alertColor }: GraphSummaryProps) => {
  return (
    <Grid item mt={smallView ? '-10px' : ''} display='flex' flexDirection='column'>
      <Grid
        data-testid='graph-summary'
        color='vitals.green'
        width='fit-content'
        sx={{
          backgroundColor: '#010101',
          height: smallView ? 18 : 22,
          marginBottom: smallView ? 0 : 9,
        }}
      >
        <Typography variant={smallView ? 'subtitle2' : 'h4'}>HR (bpm)</Typography>
      </Grid>
      <Grid display='flex' flex={1} flexDirection='row' alignItems='center'>
        <Grid
          item
          sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', mr: 8 }}
          gap={smallView ? 1 : 4}
        >
          <ThresholdText textAlign='right' smallView={smallView}>
            {data.highLimit}
          </ThresholdText>
          <ThresholdText smallView={smallView} textAlign='right'>
            {data.lowLimit}
          </ThresholdText>
        </Grid>
        <Grid item sx={{ display: 'flex', alignItems: 'center' }}>
          <Typography
            sx={{
              fontSize: smallView ? 38 : 64,
              fontWeight: 500,
              lineHeight: smallView ? '46px' : '74px',
              color: alertColor,
              marginY: '-12px',
            }}
            textAlign='right'
          >
            {data.hr}
          </Typography>
        </Grid>
      </Grid>
    </Grid>
  );
};

export default GraphSummary;
