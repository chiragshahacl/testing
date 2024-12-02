import Button from '@mui/material/Button';
import DialogContent from '@mui/material/DialogContent';
import Modal from '@mui/material/Modal';
import { useRef } from 'react';
import ConfirmationModalContainer from './container/ConfirmationModalContainer';

interface FinishBedAssignmentConfirmationModalProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
}

const FinishBedAssignmentConfirmationModal = ({
  open,
  onClose,
  onConfirm,
}: FinishBedAssignmentConfirmationModalProps) => {
  const modalRef = useRef<HTMLDivElement>(null);

  return (
    <Modal
      open={open}
      sx={{ display: 'flex', flex: 1 }}
      data-testid='finish-assignment-confirmation'
    >
      <DialogContent sx={{ margin: 'auto', outline: 'none' }}>
        <ConfirmationModalContainer
          ref={modalRef}
          title='Confirmation required'
          description='Not all patient monitors have been assigned a bed ID. Please confirm before continuing.'
        >
          <Button
            variant='contained'
            fullWidth
            onClick={onConfirm}
            sx={{ marginBottom: 24 }}
            data-testid='confirm'
          >
            Confirm
          </Button>
          <Button variant='outlined' fullWidth onClick={onClose}>
            Back to edit
          </Button>
        </ConfirmationModalContainer>
      </DialogContent>
    </Modal>
  );
};

export default FinishBedAssignmentConfirmationModal;
