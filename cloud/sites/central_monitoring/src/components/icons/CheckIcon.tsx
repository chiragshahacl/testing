import { useTheme } from '@mui/material/styles';

interface UncheckedIconProps {
  disabled?: boolean;
}

const UncheckedIcon = ({ disabled }: UncheckedIconProps) => {
  return (
    <svg width='16' height='16' viewBox='0 0 16 16' fill='none' xmlns='http://www.w3.org/2000/svg'>
      <rect
        x='0.666667'
        y='0.666667'
        width='14.6667'
        height='14.6667'
        rx='2.66667'
        stroke={disabled ? 'rgb(242, 244, 246, 0.2)' : 'rgb(242, 244, 246)'}
        strokeWidth='1.33333'
      />
    </svg>
  );
};

const CheckedIcon = () => {
  const theme = useTheme();

  return (
    <svg width='16' height='16' viewBox='0 0 16 16' fill='none' xmlns='http://www.w3.org/2000/svg'>
      <path
        fillRule='evenodd'
        clipRule='evenodd'
        d='M3.33333 0C1.49238 0 0 1.49238 0 3.33333V12.6667C0 14.5076 1.49238 16 3.33333 16H12.6667C14.5076 16 16 14.5076 16 12.6667V3.33333C16 1.49238 14.5076 0 12.6667 0H3.33333ZM12.6667 5.84596L7.16374 12L3.33333 8.81585L4.55566 7.44891L6.96744 9.45361L11.2479 4.66667L12.6667 5.84596Z'
        fill={theme.palette.primary.light}
      />
    </svg>
  );
};

export { CheckedIcon, UncheckedIcon };
