'use client';

import ItLogo from '@/components/icons/ItLogo';
import LogoutIcon from '@/components/icons/LogoutIcon';
import useSession from '@/hooks/useSession';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';

const LowerTopbar = () => {
  const { clearSession } = useSession();

  return (
    <Box position='relative'>
      <Grid
        item
        container
        direction='row'
        justifyContent='space-between'
        alignItems='center'
        sx={{
          backgroundColor: 'secondary.main',
          paddingX: 16,
        }}
      >
        <ItLogo />
        <Grid
          item
          display='flex'
          padding={(theme) => theme.spacing(12, 4)}
          onClick={clearSession}
          data-testid='logout-button'
        >
          <LogoutIcon />
          <Typography
            variant='h6'
            lineHeight='18px'
            alignSelf='center'
            color={(theme) => theme.palette.grey[600]}
          >
            Logout
          </Typography>
        </Grid>
      </Grid>
      <Box
        className='topbar-border'
        sx={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
        }}
      />
    </Box>
  );
};

export default LowerTopbar;
