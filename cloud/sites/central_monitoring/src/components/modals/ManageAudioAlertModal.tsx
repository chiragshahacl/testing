import AudioOn from '@/components/icons/AudioOn';
import CloseIcon from '@/components/icons/CloseIcon';
import { ALERT_AUDIO } from '@/constants';
import useAudioManager from '@/hooks/useAudioManager';
import { openSansFont } from '@/utils/fonts';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import Modal from '@mui/material/Modal';
import Typography from '@mui/material/Typography';
import { styled, Theme, useTheme } from '@mui/material/styles';
import AudioOff from '../icons/AudioOff';
import { StyledModalContainer } from '@/styles/StyledComponents';

const SwitchButton = styled(Grid)(() => ({
  display: 'flex',
  flex: 1,
  flexDirection: 'row',
  justifyContent: 'center',
  padding: '12px 29px',
  width: '158px',
  borderRadius: '42px',
}));

type ManageAudioAlertModalProps = {
  audioSetting: ALERT_AUDIO;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: () => void;
  onChangeAudioSetting: () => void;
};

const ManageAudioAlertModal = ({
  audioSetting,
  isOpen,
  onClose,
  onSubmit,
  onChangeAudioSetting,
}: ManageAudioAlertModalProps) => {
  const { audioAlarmSetting } = useAudioManager();
  const theme = useTheme();

  return (
    <Modal open={isOpen} sx={{ display: 'flex', flex: 1 }}>
      <StyledModalContainer container item lg={5}>
        <Grid
          item
          display='flex'
          flexDirection='row'
          justifyContent='space-between'
          alignItems='center'
          sx={{ width: '100%', mb: 24 }}
        >
          <Typography variant='h1'>Manage audio alarm</Typography>
          <CloseIcon handleClick={onClose} />
        </Grid>
        <Grid
          display='flex'
          flexDirection='row'
          justifyContent='flex-start'
          sx={{
            my: 48,
            borderRadius: 42,
            border: '2px solid #A8ADB3',
          }}
          onClick={onChangeAudioSetting}
          data-testid={`${audioSetting}`}
        >
          <SwitchButton
            sx={{
              backgroundColor: (theme: Theme) =>
                audioSetting === ALERT_AUDIO.OFF ? theme.palette.grey[700] : 'transparent',
              marginRight: '-16px',
            }}
          >
            <AudioOff
              color={
                audioSetting === ALERT_AUDIO.OFF
                  ? theme.palette.secondary.dark
                  : theme.palette.grey[800]
              }
            />
            <Typography
              color={(theme) =>
                audioSetting === ALERT_AUDIO.OFF
                  ? theme.palette.secondary.dark
                  : theme.palette.grey[800]
              }
              sx={{
                marginLeft: 8,
                fontFamily: openSansFont.style.fontFamily,
                fontSize: 16,
                fontWeight: 700,
              }}
            >
              OFF
            </Typography>
          </SwitchButton>
          <SwitchButton
            sx={{
              backgroundColor:
                audioSetting !== ALERT_AUDIO.OFF ? 'background.active' : 'transparent',
              marginLeft: '-16px',
            }}
          >
            <AudioOn
              color={
                audioSetting !== ALERT_AUDIO.OFF
                  ? theme.palette.common.white
                  : theme.palette.grey[800]
              }
            />
            <Typography
              color={(theme) =>
                audioSetting !== ALERT_AUDIO.OFF
                  ? theme.palette.common.white
                  : theme.palette.grey[800]
              }
              sx={{
                marginLeft: 8,
                fontFamily: openSansFont.style.fontFamily,
                fontSize: 16,
                fontWeight: 700,
              }}
            >
              ON
            </Typography>
          </SwitchButton>
        </Grid>
        <Button
          type='submit'
          variant='contained'
          fullWidth
          disabled={audioSetting === audioAlarmSetting}
          onClick={onSubmit}
          data-testid='save-button'
        >
          Save
        </Button>
      </StyledModalContainer>
    </Modal>
  );
};

export default ManageAudioAlertModal;
