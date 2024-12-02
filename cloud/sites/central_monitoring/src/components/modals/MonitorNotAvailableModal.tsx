import { StyledModalContainer } from '@/styles/StyledComponents';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import Modal from '@mui/material/Modal';
import Typography from '@mui/material/Typography';
import { HighAlertIcon } from '../icons/AlertIcon';

interface MonitorNotAvailableModalProps {
  isOpen: boolean;
  onConfirm: () => Promise<void> | void;
}

const MonitorNotAvailableModal = ({ isOpen, onConfirm }: MonitorNotAvailableModalProps) => {
  return (
    <Modal open={isOpen} sx={{ display: 'flex', flex: 1 }}>
      <StyledModalContainer container item lg={5}>
        <Grid
          item
          display='flex'
          flexDirection='row'
          alignItems='center'
          sx={{ width: '100%' }}
          gap='8px'
        >
          <HighAlertIcon size='32px' />
          <Typography variant='h1'>Monitor not available</Typography>
        </Grid>
        <Typography variant='subtitle1' sx={{ marginTop: '16px', marginBottom: '52px' }}>
          The patient monitor is not available at the moment. Please select another patient monitor
          or try again later.
        </Typography>
        <Grid gap='24px' display='flex' flexDirection='column' width='100%'>
          <Button variant='contained' onClick={() => void onConfirm()}>
            Ok
          </Button>
        </Grid>
      </StyledModalContainer>
    </Modal>
  );
};

export default MonitorNotAvailableModal;
