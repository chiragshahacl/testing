import { StyledTextField } from '@/styles/StyledComponents';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import React, { ChangeEvent, useState } from 'react';
import { styled } from '@mui/material/styles';
import { openSansFont } from '@/utils/fonts';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Grid from '@mui/material/Grid';
import DropdownIcon from '@/components/icons/DropdownIcon';
import { PatientGender } from '@/types/patient';
import EHRDatePicker from './EHRDatePicker';

const FieldTitle = styled(Typography)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'row',
  gap: '5px',
  marginBottom: '3px',
  fontSize: '16px',
  fontWeight: '700',
  lineHeight: '21.79px',
  fontFamily: openSansFont.style.fontFamily,
  color: theme.palette.grey[600],
}));

const FieldRequiredText = styled(Typography)(({ theme }) => ({
  lineHeight: '21.79px',
  color: theme.palette.grey[600],
  fontFamily: openSansFont.style.fontFamily,
  fontSize: '14px',
  fontWeight: '700',
}));

const CustomTextField = styled(StyledTextField)(({ theme }) => ({
  '& input::placeholder': {
    color: theme.palette.grey[600],
  },
}));

const StyledMenuItem = styled(MenuItem)(() => ({
  color: '#EFF0F1',
  fontFamily: openSansFont.style.fontFamily,
  fontSize: 18,
  fontWeight: 400,
  lineHeight: '27px',
}));

interface EHRSearchFieldProps {
  name: string;
  error?: string;
  title: string;
  id: string;
  onChange?: (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  onDateChange?: (name: string, value: string) => void;
  onSelect?: (e: SelectChangeEvent) => void;
  type?: string;
  value?: string;
  required?: boolean;
  placeholder?: string;
}

const EHRSearchField = ({
  name,
  error,
  title,
  id,
  onChange,
  onDateChange,
  onSelect,
  value,
  required,
  placeholder,
  type = 'text',
}: EHRSearchFieldProps) => {
  const [popoverOpen, setPopoverOpen] = useState(false);

  return (
    <Box width='55%'>
      <Box height={24} />
      <FieldTitle>
        {title}
        <FieldRequiredText variant='caption'>
          {required ? '(Required)' : '(Optional)'}
        </FieldRequiredText>
      </FieldTitle>
      {type === 'select' ? (
        <>
          <Select
            id={id}
            value={value}
            displayEmpty
            fullWidth
            onChange={onSelect}
            onOpen={() => setPopoverOpen(true)}
            onClose={() => setPopoverOpen(false)}
            name={name}
            sx={{
              border: (theme) => `1px solid ${theme.palette.grey[600]}`,
              borderRadius: 16,
              '& .MuiSelect-icon': {
                display: 'none',
              },
              '&.MuiOutlinedInput-root': {
                '& fieldset': {
                  border: 0,
                },
                '&:hover fieldset': {
                  border: 0,
                },
                '&.Mui-focused fieldset': {
                  border: 0,
                },
              },
            }}
            MenuProps={{
              anchorOrigin: { vertical: 'top', horizontal: 'left' },
              transformOrigin: { vertical: 'top', horizontal: 'left' },
              PaperProps: {
                sx: {
                  backgroundImage: 'none',
                  backgroundColor: 'transparent',
                },
              },
              MenuListProps: {
                sx: {
                  backgroundColor: 'primary.dark',
                  border: (theme) => `1px solid ${theme.palette.grey[600]}`,
                  borderRadius: 16,
                  overflow: 'hidden',
                },
              },
            }}
          >
            <StyledMenuItem>
              <Grid display='flex' flex={1} flexDirection='row' justifyContent='space-between'>
                <Typography>Select</Typography>
                <DropdownIcon />
              </Grid>
            </StyledMenuItem>
            <StyledMenuItem value={PatientGender.MALE}>Male</StyledMenuItem>
            <StyledMenuItem value={PatientGender.FEMALE}>Female</StyledMenuItem>
            <StyledMenuItem value={PatientGender.OTHER}>Other</StyledMenuItem>
            <StyledMenuItem value={PatientGender.UNKNOWN}>Unknown</StyledMenuItem>
          </Select>
          <Box height={popoverOpen ? 140 : 0} />
        </>
      ) : type === 'dob' ? (
        <EHRDatePicker name={name} onChange={onDateChange} error={!!error} />
      ) : (
        <CustomTextField
          name={name}
          error={!!error}
          fullWidth
          id={id}
          onChange={onChange}
          value={value}
          variant='outlined'
          type={type}
          {...(type === 'dob' && {
            inputProps: {
              maxLength: 10,
              placeholder: placeholder,
            },
          })}
        />
      )}
      {error && (
        <>
          <Typography variant='error'>{error}</Typography>
        </>
      )}
    </Box>
  );
};

export default EHRSearchField;
