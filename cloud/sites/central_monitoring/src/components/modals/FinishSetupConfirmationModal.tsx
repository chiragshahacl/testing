import Button from '@mui/material/Button';
import DialogContent from '@mui/material/DialogContent';
import Modal from '@mui/material/Modal';
import { useRef } from 'react';
import ConfirmationModalContainer from './container/ConfirmationModalContainer';

interface FinishSetupConfirmationModalProps {
  open: boolean;
  handleClose: () => void;
  handleConfirm: () => void;
}

const FinishSetupConfirmationModal = ({
  open,
  handleClose,
  handleConfirm,
}: FinishSetupConfirmationModalProps) => {
  const modalRef = useRef<HTMLDivElement>(null);

  return (
    <Modal open={open} sx={{ display: 'flex', flex: 1 }} data-testid='finish-setup-confirmation'>
      <DialogContent sx={{ margin: 'auto', outline: 'none' }}>
        <ConfirmationModalContainer
          ref={modalRef}
          title='Confirmation required'
          description='Not all beds have been assigned to a group. Please confirm before continuing.'
        >
          <Button
            variant='contained'
            fullWidth
            onClick={handleConfirm}
            sx={{ marginBottom: 24 }}
            data-testid='Confirm'
          >
            Confirm
          </Button>
          <Button variant='outlined' fullWidth onClick={handleClose}>
            Back to edit
          </Button>
        </ConfirmationModalContainer>
      </DialogContent>
    </Modal>
  );
};

export default FinishSetupConfirmationModal;
