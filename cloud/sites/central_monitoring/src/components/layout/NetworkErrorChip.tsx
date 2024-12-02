'use client';

import Typography from '@mui/material/Typography';
import { alpha } from '@mui/material/styles';
import { HighAlertIcon } from '../icons/AlertIcon';
import { StyledChip } from '@/styles/StyledComponents';

interface NetworkErrorChipProps {
  text: string;
}

const NetworkErrorChip = ({ text }: NetworkErrorChipProps): JSX.Element => {
  return (
    <StyledChip
      display='flex'
      flexDirection='row'
      sx={{
        backgroundColor: (theme) => alpha(theme.palette['error']['main'], 0.25),
      }}
    >
      <HighAlertIcon />
      <Typography variant='caption'>{text}</Typography>
    </StyledChip>
  );
};

export default NetworkErrorChip;
