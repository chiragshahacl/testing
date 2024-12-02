import React from 'react';

const LeftArrowIcon = ({ color }: { color?: string }) => {
  return (
    <svg
      data-testid='left-arrow'
      width='11'
      height='20'
      viewBox='0 0 11 20'
      fill='none'
      xmlns='http://www.w3.org/2000/svg'
    >
      <path
        d='M9.5 18.1666L1.33333 9.99992L9.5 1.83325'
        stroke={color || 'white'}
        strokeWidth='2.33333'
        strokeLinecap='round'
        strokeLinejoin='round'
      />
    </svg>
  );
};

const RightArrowIcon = () => {
  return (
    <svg
      data-testid='right-arrow'
      width='11'
      height='20'
      viewBox='0 0 11 20'
      fill='none'
      xmlns='http://www.w3.org/2000/svg'
    >
      <path
        d='M1.5 1.83341L9.66667 10.0001L1.5 18.1667'
        stroke='white'
        strokeWidth='2.33333'
        strokeLinecap='round'
        strokeLinejoin='round'
      />
    </svg>
  );
};

export { RightArrowIcon, LeftArrowIcon };
