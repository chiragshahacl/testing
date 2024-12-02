import { useBeds } from '@/api/useBeds';
import { useGroups } from '@/api/useGroups';
import { usePatientMonitors } from '@/api/usePatientMonitors';
import ConfirmationModalContainer from '@/components/modals/container/ConfirmationModalContainer';
import { ALERT_AUDIO } from '@/constants';
import useAudioManager from '@/hooks/useAudioManager';
import Button from '@mui/material/Button';
import DialogContent from '@mui/material/DialogContent';
import Modal from '@mui/material/Modal';
import { useRef } from 'react';

const AlertEnabledModal = () => {
  const {
    activeAlertsExist,
    audioAlarmSetting,
    audioIsActive,
    startCurrentAudioFile,
    autoPlayActivated,
    setAutoPlayActivated,
  } = useAudioManager();
  const modalRef = useRef<HTMLDivElement>(null);

  const beds = useBeds();
  const patientMonitors = usePatientMonitors();
  const bedGroups = useGroups();

  const initialSetupFinished =
    !beds.isPlaceholderData &&
    beds.isSuccess &&
    !patientMonitors.isPlaceholderData &&
    patientMonitors.isSuccess &&
    !bedGroups.isPlaceholderData &&
    bedGroups.isSuccess &&
    beds.data.length !== 0 &&
    patientMonitors.data.some((monitor) => !!monitor.assignedBedId) &&
    bedGroups.data.length !== 0;

  const handleConfirm = () => {
    setAutoPlayActivated(true);
    if (activeAlertsExist) startCurrentAudioFile();
  };

  return (
    <Modal
      open={
        audioAlarmSetting === ALERT_AUDIO.ON &&
        audioIsActive &&
        !autoPlayActivated &&
        initialSetupFinished
      }
      sx={{ display: 'flex', flex: 1 }}
      disableAutoFocus
    >
      <DialogContent sx={{ margin: 'auto', outline: 'none' }}>
        <ConfirmationModalContainer
          ref={modalRef}
          title='Audio alarm is enabled'
          description='You can pause audio alarms in the navigation menu or disable audio alarms in the settings.'
        >
          <Button variant='contained' fullWidth onClick={handleConfirm} sx={{ marginBottom: 24 }}>
            OK
          </Button>
        </ConfirmationModalContainer>
      </DialogContent>
    </Modal>
  );
};

export default AlertEnabledModal;
