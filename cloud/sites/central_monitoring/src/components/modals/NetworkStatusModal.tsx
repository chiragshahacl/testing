'use client';

import ConfirmationModalContainer from '@/components/modals/container/ConfirmationModalContainer';
import Button from '@mui/material/Button';
import DialogContent from '@mui/material/DialogContent';
import Modal from '@mui/material/Modal';
import { alpha } from '@mui/system';
import { useEffect, useRef, useState } from 'react';

interface NetworkStatusModalProps {
  isOnline: boolean;
  onLostConnection: () => void;
  onConfirm: () => void;
  title: string;
  description: string;
  confirmButtonText?: string;
}

const NetworkStatusModal = ({
  isOnline,
  onLostConnection,
  onConfirm,
  title,
  description,
  confirmButtonText = 'Ok',
}: NetworkStatusModalProps) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const [isOpen, setIsOpen] = useState<boolean>(false);

  useEffect(() => {
    // Automatically opens modal when network error is detected
    if (!isOnline) {
      setIsOpen(true);
      onLostConnection();
    }
  }, [isOnline, isOpen, onLostConnection]);

  return (
    <Modal
      open={isOpen}
      sx={{
        '& .MuiBackdrop-root': {
          backgroundColor: (theme) => alpha(theme.palette.common.black, 0.5),
          marginTop: 46,
        },
        display: 'flex',
        flex: 1,
      }}
      disableAutoFocus
    >
      <>
        <DialogContent sx={{ margin: 'auto', outline: 'none' }}>
          <ConfirmationModalContainer ref={modalRef} title={title} description={description}>
            <Button
              variant='contained'
              fullWidth
              onClick={() => {
                if (isOnline) {
                  onConfirm();
                  setIsOpen(false);
                }
              }}
              sx={{ marginBottom: 3 }}
            >
              {confirmButtonText}
            </Button>
          </ConfirmationModalContainer>
        </DialogContent>
      </>
    </Modal>
  );
};

export default NetworkStatusModal;
