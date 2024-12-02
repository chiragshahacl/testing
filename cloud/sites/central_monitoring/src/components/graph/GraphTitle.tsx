import Grid from '@mui/material/Grid';
import { styled } from '@mui/material/styles';

const GraphTitle = styled(Grid)(() => ({
  position: 'absolute',
  top: 10,
  left: 10,
  fontFamily: 'var(--open-sans-font)',
  fontStyle: 'normal',
  fontWeight: 400,
  fontSize: '17px',
  lineGeight: '20px',
  display: 'flex',
  alignItems: 'center',
  zIndex: 2,
}));

export default GraphTitle;
