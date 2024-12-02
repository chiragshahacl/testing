import { StyledModalContainer } from '@/styles/StyledComponents';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import Modal from '@mui/material/Modal';
import Typography from '@mui/material/Typography';
import { HighAlertIcon } from '../../icons/AlertIcon';

interface AgeWarningModalProps {
  isOpen: boolean;
  onCancel: () => void;
  onConfirm: () => Promise<void>;
}

const AgeWarningModal = ({ isOpen, onCancel, onConfirm }: AgeWarningModalProps) => {
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
          <Typography variant='h1'>Age Warning</Typography>
        </Grid>
        <Typography variant='subtitle1' sx={{ marginTop: '16px', marginBottom: '52px' }}>
          The patient must be 12 years or older to be monitored with ANNE One.
        </Typography>
        <Grid gap='24px' display='flex' flexDirection='column' width='100%'>
          <Button variant='contained' onClick={() => void onConfirm()}>
            Confirm
          </Button>
          <Button variant='outlined' onClick={onCancel}>
            Cancel
          </Button>
        </Grid>
      </StyledModalContainer>
    </Modal>
  );
};

export default AgeWarningModal;
