'use client';

import Typography from '@mui/material/Typography';
import { useMemo } from 'react';
import { BedsideAudioAlarmStatus } from '@/types/alerts';
import BedsideAudioStoppedIcon from '../icons/BedsideAudioStoppedIcon';
import { styled, useTheme } from '@mui/material/styles';
import Grid from '@mui/material/Grid';

interface BedsideAudioAlarmStatusChipProps {
  status?: BedsideAudioAlarmStatus;
}

export const StyledBedsideChip = styled(Grid)(({ theme }) => ({
  gap: 4.25,
  borderRadius: 16,
  backgroundColor: 'transparent',
  border: '2px',
  borderStyle: 'solid',
  borderColor: theme.palette.primary.main,
  padding: '8px',
}));

const BedsideAudioAlarmStatusChip = ({ status }: BedsideAudioAlarmStatusChipProps): JSX.Element => {
  const theme = useTheme();
  const displayText = useMemo(() => {
    switch (status) {
      case BedsideAudioAlarmStatus.PAUSED:
        return 'Audio Paused at bedside';
      case BedsideAudioAlarmStatus.OFF:
        return 'Audio Off at bedside';
      default:
        return undefined;
    }
  }, [status]);

  if (!displayText) return <></>;
  return (
    <StyledBedsideChip display='flex' flexDirection='row'>
      <BedsideAudioStoppedIcon />
      <Typography
        variant='h6'
        sx={{
          color: theme.palette.primary.main,
        }}
      >
        {displayText}
      </Typography>
    </StyledBedsideChip>
  );
};

export default BedsideAudioAlarmStatusChip;
