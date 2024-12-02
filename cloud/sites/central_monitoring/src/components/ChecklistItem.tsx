import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import CompleteIcon from './icons/CompleteIcon';
import IncompleteIcon from './icons/IncompleteIcon';

interface ChecklistItemProps {
  active: boolean;
  children: string;
}

const ChecklistItem = ({ active, children }: ChecklistItemProps) => {
  return (
    <Box display='flex' flexDirection='row' mt='5px'>
      {active ? <CompleteIcon /> : <IncompleteIcon />}
      <Typography>{children}</Typography>
    </Box>
  );
};

export default ChecklistItem;
