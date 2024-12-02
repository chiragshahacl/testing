import { StyledModalContainer } from '@/styles/StyledComponents';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import Modal from '@mui/material/Modal';
import Typography from '@mui/material/Typography';

interface AdmissionRejectedModalProps {
  isOpen: boolean;
  onConfirm: () => Promise<void>;
}

const AdmissionRejectedModal = ({ isOpen, onConfirm }: AdmissionRejectedModalProps) => {
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
          <Typography variant='h1'>Admission Rejected</Typography>
        </Grid>
        <Typography variant='subtitle1' sx={{ marginTop: '16px', marginBottom: '52px' }}>
          The admission request was rejected at the bedside patient monitor.
        </Typography>
        <Grid gap='24px' display='flex' flexDirection='column' width='100%'>
          <Button variant='contained' onClick={() => void onConfirm()}>
            Back to admit
          </Button>
        </Grid>
      </StyledModalContainer>
    </Modal>
  );
};

export default AdmissionRejectedModal;
