import { styled, useTheme } from '@mui/material/styles';
import TextField from '@mui/material/TextField';
import { useEffect, useRef } from 'react';

const CustomDisableInput = styled(TextField)(({ theme }) => ({
  '.MuiInputBase-input.Mui-disabled.active': {
    WebkitTextFillColor: theme.palette.primary.dark,
    color: theme.palette.primary.dark,
    textOverflow: 'ellipsis',
    margin: theme.spacing(0, 8),
  },
  '.MuiInputBase-input.Mui-disabled.inactive': {
    WebkitTextFillColor: theme.palette.grey[200],
    color: theme.palette.grey[200],
    textOverflow: 'ellipsis',
    margin: theme.spacing(0, 8),
  },
}));

type ItemId = string;

interface EditableListItemProps {
  item: { id: ItemId; name: string };
  isActive: boolean;
  isEditing: boolean;
  hasError: boolean;
  onNameChange: (id: ItemId, name: string) => void;
  onFinishEditing: (id: ItemId, name: string) => void;
}

const EditableListItem = ({
  item,
  isActive,
  isEditing,
  hasError,
  onNameChange,
  onFinishEditing,
}: EditableListItemProps) => {
  const inputRef = useRef<HTMLElement>();
  const theme = useTheme();

  useEffect(() => {
    // Automatically focus input if it's set to be editted
    if (isEditing) inputRef.current?.focus();
  }, [isEditing]);

  return (
    <CustomDisableInput
      autoFocus={isEditing}
      inputRef={inputRef}
      defaultValue={item.name}
      margin='none'
      variant='standard'
      disabled={!isEditing}
      inputProps={{
        'aria-label': item.name,
        className: isActive && !hasError ? 'active' : 'inactive',
      }}
      InputProps={{
        disableUnderline: true,
        style: {
          fontSize: 17,
          fontWeight: (isActive && !hasError) || (isEditing && hasError) ? '700' : '400',
          lineHeight: 20,
          color: hasError ? theme.palette.error.dark : theme.palette.common.white,
          marginTop: hasError && isEditing ? '-2px' : '1px',
          pointerEvents: isEditing ? 'auto' : 'none',
        },
        onBlur: (e: { target: { value: string } }) => {
          onFinishEditing(item.id, e.target.value);
          if (!e.target.value) {
            inputRef.current?.focus();
          }
        },
        onChange: (e: { target: { value: string } }) => onNameChange(item.id, e.target.value),
      }}
      sx={{ input: { textAlign: 'center' } }}
    />
  );
};

export default EditableListItem;
