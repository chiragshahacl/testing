import ConfirmationModalContainer from '@/components/modals/container/ConfirmationModalContainer';
import Button from '@mui/material/Button';
import DialogContent from '@mui/material/DialogContent';
import Modal from '@mui/material/Modal';
import { useRef } from 'react';

interface PasswordChangedModalProps {
  onClose: () => void;
}

const PasswordChangedModal = ({ onClose }: PasswordChangedModalProps) => {
  const modalRef = useRef<HTMLDivElement>(null);

  return (
    <Modal open sx={{ display: 'flex', flex: 1 }}>
      <DialogContent sx={{ margin: 'auto', outline: 'none' }}>
        <ConfirmationModalContainer
          ref={modalRef}
          title='Password changed'
          description='Your password has been successfully changed. Please use your new password for future logins.'
        >
          <Button variant='contained' fullWidth onClick={onClose} sx={{ marginBottom: 24 }}>
            Ok
          </Button>
        </ConfirmationModalContainer>
      </DialogContent>
    </Modal>
  );
};

export default PasswordChangedModal;
