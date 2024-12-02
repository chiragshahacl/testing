import ChangePassword from '@/components/Settings/ChangePassword';
import AccountIcon from '@/components/icons/AccountIcon';
import LogoutModal from '@/components/modals/LogoutModal';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { useState } from 'react';
import ManageAudioAlert from './ManageAudioAlert';

const SettingsSidebar = () => {
  const [manageAudioAlertOpen, setManageAudioAlertOpen] = useState<boolean>(false);
  const [logoutOpen, setLogoutOpen] = useState<boolean>(false);
  const [changePasswordOpen, setChangePasswordOpen] = useState<boolean>(false);

  const onLogoutOpen = () => {
    setLogoutOpen(true);
  };

  const onLogoutClose = () => {
    setLogoutOpen(false);
  };

  const onChangePasswordOpen = () => {
    setChangePasswordOpen(true);
  };
  const onChangePasswordClose = () => {
    setChangePasswordOpen(false);
  };
  const onManageAudioAlarm = () => {
    setManageAudioAlertOpen(true);
  };

  return (
    <>
      <LogoutModal isOpen={logoutOpen} onClose={onLogoutClose} />
      <ChangePassword isOpen={changePasswordOpen} onClose={onChangePasswordClose} />
      <ManageAudioAlert isOpen={manageAudioAlertOpen} onSetOpen={setManageAudioAlertOpen} />

      <Grid
        sx={{
          width: 60,
          backgroundColor: 'primary.dark',
          paddingY: 16,
        }}
      >
        <Grid
          display='flex'
          flexDirection='column'
          alignItems='center'
          sx={{
            width: '100%',
            backgroundColor: 'background.modal',
            padding: (theme) => theme.spacing(6, 0, 4),
          }}
        >
          <AccountIcon />
          <Typography variant='subtitle2'>Admin</Typography>
        </Grid>
      </Grid>
      <Grid
        item
        display='flex'
        flexDirection='column'
        sx={{
          flex: 1,
          padding: (theme) => theme.spacing(60, 14),
          backgroundColor: 'background.modal',
        }}
      >
        <Button variant='outlined' onClick={onManageAudioAlarm}>
          Manage audio alarm
        </Button>
        <Box height={24} />
        <Button variant='outlined' onClick={onChangePasswordOpen}>
          Change password
        </Button>
        <Box height={24} />
        <Button variant='contained' onClick={onLogoutOpen}>
          Log out
        </Button>
      </Grid>
    </>
  );
};

export default SettingsSidebar;
