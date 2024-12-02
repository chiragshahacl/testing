import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import React from 'react';
import { styled } from '@mui/material/styles';

const FieldNameText = styled(Typography)(({ theme }) => ({
  fontSize: 18,
  fontWeight: '400',
  lineHeight: '32.68px',
  color: theme.palette.common.white,
  width: '25%',
}));

const ValueText = styled(Typography)(({ theme }) => ({
  fontSize: 24,
  fontWeight: '700',
  lineHeight: '32.68px',
  color: theme.palette.grey[600],
  textTransform: 'capitalize',
}));

interface EHRAdmitInfoLineProps {
  fieldName: string;
  value?: string;
}

const EHRAdmitInfoLine = ({ fieldName, value }: EHRAdmitInfoLineProps) => {
  return (
    <Box width='100%' flexDirection='row' display='flex' height='45px'>
      <FieldNameText>{fieldName}</FieldNameText>
      <ValueText>{value}</ValueText>
    </Box>
  );
};

export default EHRAdmitInfoLine;
