import Grid from '@mui/material/Grid';
import { SignalIcon } from './Signalicon';

interface SignalIndicatorProps {
  signal: number;
}

const SignalIndicator = ({ signal }: SignalIndicatorProps) => {
  return (
    <Grid flex={1} my='-5px'>
      <SignalIcon signal={signal} />
    </Grid>
  );
};

export default SignalIndicator;
