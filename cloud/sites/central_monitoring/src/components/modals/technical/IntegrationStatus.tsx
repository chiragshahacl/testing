import Button from '@mui/material/Button';
import DialogContent from '@mui/material/DialogContent';
import Modal from '@mui/material/Modal';
import { useRef } from 'react';
import Box from '@mui/material/Box';
import { StyledModalContainer } from '@/styles/StyledComponents';
import Typography from '@mui/material/Typography';
import IntegrationFailedIcon from '@/components/icons/IntegrationFailedIcon';
import IntegrationCompleteIcon from '@/components/icons/IntegrationCompleteIcon';

interface IntegrationStatusModalProps {
  open: boolean;
  successStatus: boolean;
  handleClose: () => void;
}

const IntegrationStatus = ({ open, handleClose, successStatus }: IntegrationStatusModalProps) => {
  const modalRef = useRef<HTMLDivElement>(null);

  return (
    <Modal open={open} sx={{ display: 'flex', flex: 1 }} data-testid={'ehr-integration-failed'}>
      <DialogContent sx={{ margin: 'auto', outline: 'none' }}>
        <StyledModalContainer
          ref={modalRef}
          container
          item
          lg={5}
          sx={{
            flexDirection: 'column',
            width: 561,
          }}
        >
          <Box mb={10} alignSelf='center'>
            {successStatus ? <IntegrationCompleteIcon /> : <IntegrationFailedIcon />}
          </Box>
          <Typography variant='h1'>
            {successStatus ? 'Integration Completed' : 'Integration Failed'}
          </Typography>
          <Typography variant='subtitle1' sx={{ marginY: 24 }}>
            {successStatus
              ? 'The server is now connected to EHR.'
              : 'Please double check the parameters and try again.'}
          </Typography>
          <Button variant='contained' fullWidth onClick={handleClose}>
            {successStatus ? 'Ok' : 'Back to edit'}
          </Button>
        </StyledModalContainer>
      </DialogContent>
    </Modal>
  );
};

export default IntegrationStatus;
