import React from 'react';

const DownFullArrowIcon = ({ color }: { color?: string }) => {
  return (
    <svg
      data-testid='down-full-arrow-icon'
      width='24'
      height='24'
      viewBox='0 0 24 24'
      fill='none'
      xmlns='http://www.w3.org/2000/svg'
    >
      <path d='M7 10L12 15L17 10H7Z' fill={color ? color : 'white'} />
    </svg>
  );
};

export { DownFullArrowIcon };
