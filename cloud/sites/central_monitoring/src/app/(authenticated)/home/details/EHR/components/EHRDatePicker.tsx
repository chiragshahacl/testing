import React from 'react';
import { DatePicker } from '@mui/x-date-pickers';
import { get } from 'lodash';
import { DATE_FORMAT } from '@/utils/ehr';

interface EHRDatePickerProps {
  name: string;
  onChange?: (name: string, value: string) => void;
  error: boolean;
}

const EHRDatePicker = ({ name, onChange, error }: EHRDatePickerProps) => {
  return (
    <DatePicker
      format={DATE_FORMAT}
      disableFuture
      closeOnSelect
      reduceAnimations
      disableHighlightToday
      label={null}
      className='ehrDatePicker'
      slotProps={{
        textField: {
          name: name,
          onKeyUp: (e) => {
            onChange && onChange(name, get(e.target, 'value', ''));
          },
        },
      }}
      onChange={(newDate) => {
        onChange && onChange(name, newDate?.format(DATE_FORMAT) || '');
      }}
      sx={{
        width: '100%',
        border: (theme) => `1px solid ${error ? 'red' : theme.palette.grey[600]}`,
        borderRadius: 16,
        '&:hover fieldset': {
          border: 'none',
        },
        '&:focus-visible fieldset': {
          border: 'none',
        },
        '&.Mui-focused fieldset': {
          border: 'none',
        },
      }}
    />
  );
};

export default EHRDatePicker;
