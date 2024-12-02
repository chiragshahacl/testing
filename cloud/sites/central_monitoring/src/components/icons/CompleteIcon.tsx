import React from 'react';
import Box from '@mui/material/Box';

const CompleteIcon = () => {
  return (
    <Box
      data-testid='complete-icon'
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
          d='M0 12C0 5.37258 5.37256 0 12 0C18.6274 0 24 5.37258 24 12C24 18.6274 18.6274 24 12 24C5.37256 24 0 18.6274 0 12ZM19.0864 8.51317L10.8994 18.0094L5.20073 13.096L7.01924 10.9867L10.6074 14.0801L16.9756 6.69343L19.0864 8.51317Z'
          fill='#3FC1C0'
        />
      </svg>
    </Box>
  );
};

export default CompleteIcon;
