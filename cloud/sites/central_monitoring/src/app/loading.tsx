'use client';

import CircularProgress from '@mui/material/CircularProgress';
import Grid from '@mui/material/Grid';

/**
 * Shows loading indicator
 */
const Loading = ({
  height,
  size = 64,
  thickness = 5,
  ...props
}: {
  height?: number | string;
  size?: number;
  thickness?: number;
}) => {
  return (
    <Grid
      display='flex'
      flex={1}
      justifyContent='center'
      alignItems='center'
      height={height || '100vh'}
      data-testid='loading-spinner'
      {...props}
    >
      <CircularProgress size={size} thickness={thickness} color='primary' />
    </Grid>
  );
};

export default Loading;
