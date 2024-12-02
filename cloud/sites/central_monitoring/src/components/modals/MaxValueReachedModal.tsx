import Button from '@mui/material/Button';
import Modal from '@mui/material/Modal';
import { useRef } from 'react';
import ConfirmationModalContainer from './container/ConfirmationModalContainer';
import { getCachedRuntimeConfig } from '@/utils/runtime';

interface MaxValueReachedModalProps {
  open: boolean;
  handleClose: () => void;
}

const MaxValueReachedModal = ({ open, handleClose }: MaxValueReachedModalProps) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const MAX_NUMBER_BEDS = getCachedRuntimeConfig().MAX_NUMBER_BEDS;

  return (
    <Modal open={open} sx={{ display: 'flex', flex: 1 }}>
      <ConfirmationModalContainer
        ref={modalRef}
        title='Bed limit reached'
        description={`You have reached the maximum number of beds for the system (${MAX_NUMBER_BEDS}).`}
      >
        <Button variant='contained' fullWidth onClick={handleClose} sx={{ marginBottom: 24 }}>
          Back to edit
        </Button>
      </ConfirmationModalContainer>
    </Modal>
  );
};

export default MaxValueReachedModal;
