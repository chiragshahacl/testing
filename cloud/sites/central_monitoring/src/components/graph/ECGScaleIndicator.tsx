import Typography from '@mui/material/Typography';
import React from 'react';
import { styled } from '@mui/material';

// Percentage the indicator should occupy of the graph space for a (-2.4 to 2.4) 10mV scale
const SCALE_PERCENTAGE_SIZE = 17.5;

const StyledText = styled(Typography)(() => ({
  fontFamily: 'var(--open-sans-font)',
  fontWeight: '400',
  fontSize: '17px',
  lineHeight: '250%',
}));

const ScaleIndicatorImage = () => {
  return (
    <svg height='100%' viewBox='0 0 22 46' fill='none' xmlns='http://www.w3.org/2000/svg'>
      <path d='M0 45H2.8785V1H15.215V45H22' stroke='#D7D7D7' strokeWidth='1.5' />
    </svg>
  );
};

const ECGScaleIndicator = ({
  shiftScaleRight,
  customHeight,
}: {
  shiftScaleRight: boolean;
  customHeight?: string;
}) => {
  return (
    <div
      style={{
        display: 'flex',
        left: shiftScaleRight ? '6%' : '2%',
        height: customHeight ? customHeight : `${SCALE_PERCENTAGE_SIZE}%`,
        position: 'absolute',
        top: customHeight ? 0 : `${(100 - SCALE_PERCENTAGE_SIZE) / 2}%`,
        zIndex: 1,
      }}
    >
      <ScaleIndicatorImage />
      <StyledText>1mV</StyledText>
    </div>
  );
};

export default ECGScaleIndicator;
