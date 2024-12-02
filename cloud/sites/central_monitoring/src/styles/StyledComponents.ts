import Grid from '@mui/material/Grid';
import TextField from '@mui/material/TextField';
import { styled } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { openSansFont } from '@/utils/fonts';
import theme from '@/theme/theme';

export const StyledChip = styled(Grid)(({ theme }) => ({
  gap: 4.25,
  padding: theme.spacing(8, 21),
  borderRadius: 16,
}));

export const StyledModalContainer = styled(Grid)(({ theme }) => ({
  margin: 'auto',
  backgroundColor: theme.palette.background.modal,
  padding: 32,
  borderRadius: 16,
}));

export const Content = styled(Grid)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  borderRadius: 16,
  backgroundColor: theme.palette.secondary.main,
  padding: 16,
}));

export const ContentHeader = styled(Grid)(() => ({
  display: 'flex',
  flexDirection: 'row',
  marginTop: 10,
  marginBottom: 15,
  justifyContent: 'space-between',
}));

export const PasswordTextField = styled(TextField)(({ theme, value }) => ({
  '> div': {
    fontFamily: openSansFont.style.fontFamily,
    color: '#F2F4F6',
    height: '56px',
    fontSize: value ? '34px' : '18px',
    letterSpacing: value ? '-2px' : undefined,
  },
  '&.MuiTextField-root .MuiOutlinedInput-notchedOutline': {
    border: '1px solid #F2F4F6',
    borderRadius: 16,
  },
  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
    border: '1px solid #F2F4F6',
  },
  '&.Mui-error .MuiOutlinedInput-notchedOutline': {
    border: `1px solid ${theme.palette.error.main}`,
  },
}));

export const StyledTextField = styled(TextField)(({ theme }) => ({
  '&.MuiTextField-root .MuiOutlinedInput-notchedOutline': {
    border: '1px solid #F2F4F6',
    borderRadius: 16,
  },
  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
    border: '1px solid #F2F4F6',
  },
  '&.Mui-error .MuiOutlinedInput-notchedOutline': {
    border: `1px solid ${theme.palette.error.main}`,
  },
}));

export const AlertPriorityIndicator = styled(Box)(() => ({
  display: 'flex',
  alignSelf: 'center',
  height: 12,
  width: 12,
  marginRight: 10,
  borderRadius: '50%',
}));

export const ThresholdText = styled(Typography, {
  shouldForwardProp: (prop) => prop !== 'color',
})<{ color?: string }>(({ color }) => ({
  lineHeight: '14.94px',
  color: color,
}));

ThresholdText.defaultProps = {
  display: 'flex',
  variant: 'bodySmall',
};

export const CopyrightText = styled(Typography)(({ theme }) => ({
  fontFamily: openSansFont.style.fontFamily,
  color: theme.palette.grey[700],
}));

export const LabelContainer = styled('label')(() => ({
  display: 'block',
  color: theme.palette.grey[600],
  marginBottom: 4,
}));

export const LabelText = styled('span')(() => ({
  fontSize: 16,
  fontWeight: 700,
  lineHeight: '22px',
  fontFamily: openSansFont.style.fontFamily,
}));

export const LabelHelper = styled('span')(() => ({
  fontSize: 14,
  fontWeight: 700,
  lineHeight: '22px',
  fontFamily: openSansFont.style.fontFamily,
}));

export const ErrorText = styled(Typography)(() => ({
  lineHeight: '22px',
  fontFamily: openSansFont.style.fontFamily,
  marginLeft: 12,
  display: 'block',
}));

export const Label = styled(Typography)(() => ({
  minWidth: 200,
  maxWidth: 200,
  fontFamily: openSansFont.style.fontFamily,
}));

export const Value = styled(Typography)(() => ({
  fontFamily: openSansFont.style.fontFamily,
  alignSelf: 'center',
  overflowWrap: 'anywhere',
}));

export const ModalContentScrollContainer = styled(Grid)(({ theme }) => ({
  overflowY: 'scroll',
  overflowX: 'hidden',
  flex: 1,
  '::-webkit-scrollbar': {
    width: '4px',
  },
  '::-webkit-scrollbar-thumb': {
    backgroundColor: theme.palette.grey[700],
    borderRadius: '16px',
  },
  '::-webkit-scrollbar-track': {
    backgroundColor: 'transparent',
  },
}));
