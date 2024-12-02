import Button from '@mui/material/Button';
import DialogContent from '@mui/material/DialogContent';
import Modal from '@mui/material/Modal';
import { useRef } from 'react';
import ConfirmationModalContainer from './container/ConfirmationModalContainer';

interface UnsavedModalProps {
  isOpen: boolean;
  title?: string;
  description?: string;
  onDiscard: () => void;
  onContinueEdit: () => void;
}

const UnsavedModal = ({
  isOpen,
  onDiscard,
  onContinueEdit,
  title = 'Unsaved information',
  description = 'The entered information has not been saved.',
}: UnsavedModalProps) => {
  const modalRef = useRef<HTMLDivElement>(null);

  return (
    <Modal open={isOpen} sx={{ display: 'flex', flex: 1 }}>
      <DialogContent sx={{ margin: 'auto', outline: 'none' }}>
        <ConfirmationModalContainer ref={modalRef} title={title} description={description}>
          <Button
            variant='contained'
            fullWidth
            onClick={onContinueEdit}
            sx={{ mb: 24 }}
            data-testid='back-to-edit-button'
          >
            Back to edit
          </Button>
          <Button variant='outlined' fullWidth onClick={onDiscard} data-testid='discard-button'>
            Discard
          </Button>
        </ConfirmationModalContainer>
      </DialogContent>
    </Modal>
  );
};

export default UnsavedModal;
