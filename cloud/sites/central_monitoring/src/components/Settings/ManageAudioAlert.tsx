import { getAuthErrorMessage } from '@/api/authErrors';
import { usePasswordValidation } from '@/api/usePasswordValidation';
import { ALERT_AUDIO } from '@/constants';
import useAudioManager from '@/hooks/useAudioManager';
import { ServerErrorResponse } from '@/types/response';
import { STORAGE_KEYS } from '@/utils/storage';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { FormikHelpers } from 'formik';
import { useState } from 'react';
import { HighAlertIcon } from '../icons/AlertIcon';
import AlarmSettingUpdated from '../modals/AlarmSettingUpdated';
import ManageAudioAlertModal from '../modals/ManageAudioAlertModal';
import PasswordValidationModal, { FormValues } from '../modals/PasswordValidationModal';
import UnsavedModal from '../modals/UnsavedModal';

type ManageAudioAlertProps = {
  isOpen: boolean;
  onSetOpen: (isOpen: boolean) => void;
};

const ManageAudioAlert = ({ isOpen, onSetOpen }: ManageAudioAlertProps) => {
  const { audioAlarmSetting, updateAudioSetting } = useAudioManager();
  const [audioSetting, setAudioSetting] = useState<ALERT_AUDIO>(audioAlarmSetting);
  const [isValidatePasswordOpen, setIsValidatePasswordOpen] = useState<boolean>(false);
  const [isUnsavedChangesOpen, setIsUnsavedChangesOpen] = useState<boolean>(false);
  const [alarmSettingUpdated, setAlarmSettingUpdated] = useState<boolean>(false);

  const { validate } = usePasswordValidation();

  const onCloseAlarmSettingUpdated = () => setAlarmSettingUpdated(false);

  const onBackToEdit = () => {
    if (isValidatePasswordOpen) setIsValidatePasswordOpen(false);
    if (isUnsavedChangesOpen) setIsUnsavedChangesOpen(false);
    onSetOpen(true);
  };

  const onSaveSettings = () => {
    setIsValidatePasswordOpen(true);
    onSetOpen(false);
  };

  const onValidateSubmit = async (
    values: FormValues,
    { setErrors, setSubmitting }: FormikHelpers<FormValues>
  ) => {
    const { password } = values;
    await validate(
      { password },
      {
        onSuccess: () => {
          localStorage.setItem(STORAGE_KEYS.ALERT_AUDIO_SETTING, audioSetting);
          setIsValidatePasswordOpen(false);
          setAlarmSettingUpdated(true);
          updateAudioSetting();
        },
        onError: (err: ServerErrorResponse) => {
          setErrors({ password: getAuthErrorMessage(err) });
        },
        onSettled: () => {
          setSubmitting(false);
        },
      }
    );
  };

  const onClose = () => {
    if (isOpen) onSetOpen(false);
    if (isValidatePasswordOpen) setIsValidatePasswordOpen(false);
    if (audioSetting !== audioAlarmSetting) {
      setIsUnsavedChangesOpen(true);
    }
  };

  const onChangeAudioSetting = () => {
    setAudioSetting(audioSetting === ALERT_AUDIO.ON ? ALERT_AUDIO.OFF : ALERT_AUDIO.ON);
  };

  const onDiscardUnsavedChanges = () => {
    setIsUnsavedChangesOpen(false);
    setAudioSetting(audioAlarmSetting);
  };

  if (alarmSettingUpdated) {
    return (
      <AlarmSettingUpdated isOpen={alarmSettingUpdated} onClose={onCloseAlarmSettingUpdated} />
    );
  } else if (isUnsavedChangesOpen) {
    return (
      <UnsavedModal
        isOpen={isUnsavedChangesOpen}
        title='Unsaved changes'
        description='Your changes have not been saved.'
        onDiscard={onDiscardUnsavedChanges}
        onContinueEdit={onBackToEdit}
      />
    );
  } else if (isValidatePasswordOpen) {
    return (
      <PasswordValidationModal
        isOpen={isValidatePasswordOpen}
        onClose={onClose}
        onSubmit={onValidateSubmit}
        onBack={onBackToEdit}
        description={
          <Grid display='flex' flexDirection='row' gap='8.33px' my={24}>
            <HighAlertIcon />
            <Typography variant='subtitle1'>
              All audible alarms at Central Station will be silenced until manually activated.
              Please enter the password to save alarm settings.
            </Typography>
          </Grid>
        }
      />
    );
  }

  return (
    <ManageAudioAlertModal
      audioSetting={audioSetting}
      isOpen={isOpen}
      onClose={onClose}
      onSubmit={onSaveSettings}
      onChangeAudioSetting={onChangeAudioSetting}
    />
  );
};

export default ManageAudioAlert;
