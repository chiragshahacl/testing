import Box from '@mui/material/Box';
import { useTheme } from '@mui/material/styles';

const IncompleteIcon = () => {
  const theme = useTheme();

  return (
    <Box
      data-testid='incomplete-icon'
      sx={{ mr: '6px', display: 'flex', justifyContent: 'center', width: '20px' }}
    >
      <svg
        width='24'
        height='24'
        viewBox='0 0 24 24'
        fill='none'
        xmlns='http://www.w3.org/2000/svg'
      >
        <path
          fillRule='evenodd'
          clipRule='evenodd'
          d='M12 0C18.6506 0 24 5.3494 24 12C24 18.6506 18.6506 24 12 24C5.3494 24 0 18.6506 0 12C0 5.3494 5.3494 0 12 0ZM6.07229 8.09639L8.09639 6.07229L12 9.9759L15.9036 6.07229L18 8.09639L14.0241 12L18 15.9036L15.9036 18L12 14.0241L8.09639 18L6.07229 15.9036L9.9759 12L6.07229 8.09639Z'
          fill={theme.palette.error.main}
        />
      </svg>
    </Box>
  );
};

export default IncompleteIcon;
