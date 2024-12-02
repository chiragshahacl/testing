import Loading from '@/app/loading';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { styled } from '@mui/material/styles';
import { get } from 'lodash';

const StyledThresholdText = styled(Typography, {
  shouldForwardProp: (prop) => prop !== 'color',
})<{ color?: string }>(({ color }) => ({
  fontSize: 13,
  fontWeight: 400,
  lineHeight: '15px',
  color: color,
  mb: 4,
  alignSelf: 'flex-start',
}));

const StyledLargeText = styled(Typography, {
  shouldForwardProp: (prop) => prop !== 'hasAlert' && prop !== 'color',
})<{ hasAlert?: boolean; color?: string }>(({ hasAlert, color, theme }) => ({
  fontSize: 32,
  fontWeight: 500,
  color: hasAlert ? get(theme.palette, 'alert.medium') : color,
  marginY: '-12px',
}));

interface ThreeDigitCardProps {
  title: string;
  bigData?: number | string;
  firstSmall?: number | string;
  secondSmall?: number | string;
  color?: string;
  hasAlert?: boolean;
}

const ThreeDigitCard = ({
  title,
  bigData,
  firstSmall,
  secondSmall,
  color,
  hasAlert = false,
}: ThreeDigitCardProps) => {
  return (
    <Grid key={title} sx={{ display: 'flex', flex: 1, flexDirection: 'column' }}>
      <Grid
        width='fit-content'
        sx={{
          backgroundColor: 'background.text',
          padding: (theme) => theme.spacing(1, 2, 1, 0),
        }}
      >
        <StyledThresholdText color={color}>{title}</StyledThresholdText>
      </Grid>
      <Grid item sx={{ display: 'flex', justifyContent: 'space-between', py: 4.5 }}>
        <Grid item sx={{ display: 'flex', flexDirection: 'column', mr: 8 }}>
          <StyledThresholdText textAlign='right' color={color}>
            {firstSmall}
          </StyledThresholdText>
          <StyledThresholdText textAlign='right' color={color}>
            {secondSmall}
          </StyledThresholdText>
        </Grid>
        {bigData !== null && bigData !== undefined ? (
          <Grid item sx={{ display: 'flex', alignItems: 'center' }}>
            <StyledLargeText textAlign='right' color={color} hasAlert={hasAlert}>
              {bigData}
            </StyledLargeText>
          </Grid>
        ) : (
          <Grid item sx={{ mr: 8 }}>
            <Loading height='100%' size={32} thickness={2.5} />
          </Grid>
        )}
      </Grid>
    </Grid>
  );
};

export default ThreeDigitCard;
