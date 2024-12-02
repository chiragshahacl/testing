import ConfirmationModalContainer from '@/components/modals/container/ConfirmationModalContainer';
import Button from '@mui/material/Button';
import DialogContent from '@mui/material/DialogContent';
import Modal from '@mui/material/Modal';
import { useRef } from 'react';

interface AlarmSettingUpdatedProps {
  isOpen: boolean;
  onClose: () => void;
}

const AlarmSettingUpdated = ({ isOpen, onClose }: AlarmSettingUpdatedProps) => {
  const modalRef = useRef<HTMLDivElement>(null);

  return (
    <Modal open={isOpen} sx={{ display: 'flex', flex: 1 }} disableAutoFocus>
      <DialogContent sx={{ margin: 'auto', outline: 'none' }}>
        <ConfirmationModalContainer
          ref={modalRef}
          title='Alarm settings updated'
          description='Alarm settings have been successfully updated.'
        >
          <Button variant='contained' fullWidth onClick={onClose} sx={{ marginBottom: 24 }}>
            Ok
          </Button>
        </ConfirmationModalContainer>
      </DialogContent>
    </Modal>
  );
};

export default AlarmSettingUpdated;
