import Button from '@mui/material/Button';
import DialogContent from '@mui/material/DialogContent';
import Modal from '@mui/material/Modal';
import { useRef } from 'react';
import ConfirmationModalContainer from './container/ConfirmationModalContainer';

interface GroupDeleteErrorModalProps {
  title: string;
  description: string;
  open: boolean;
  handleClose: () => void;
}

const ModifyServerErrorModal = ({
  open,
  handleClose,
  title,
  description,
}: GroupDeleteErrorModalProps) => {
  const modalRef = useRef<HTMLDivElement>(null);

  return (
    <Modal open={open} sx={{ display: 'flex', flex: 1 }} data-testid={'modify-server-error'}>
      <DialogContent sx={{ margin: 'auto', outline: 'none' }}>
        <ConfirmationModalContainer ref={modalRef} title={title} description={description}>
          <Button variant='contained' fullWidth onClick={handleClose} sx={{ marginBottom: 24 }}>
            OK
          </Button>
        </ConfirmationModalContainer>
      </DialogContent>
    </Modal>
  );
};

export default ModifyServerErrorModal;
