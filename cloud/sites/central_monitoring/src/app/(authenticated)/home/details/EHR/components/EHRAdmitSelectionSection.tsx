import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import { styled } from '@mui/material/styles';
import Typography from '@mui/material/Typography';

const ComponentContainer = styled(Box)(() => ({
  display: 'flex',
  flexDirection: 'column',
  marginBottom: 15,
  justifyContent: 'space-between',
}));

const StyledText = styled(Typography)(() => ({
  fontFamily: 'var(--open-sans-font)',
  fontWeight: '700',
  fontSize: '18px',
  lineHeight: '20.68px',
}));

const ActionButton = styled(Button)(({ theme }) => ({
  backgroundColor: theme.palette.background.active,
  fontFamily: 'var(--open-sans-font)',
  fontWeight: '700',
  fontSize: '17px',
  lineHeight: '19.53px',
  borderRadius: '16px',
  width: '150px',
  padding: '8px 16px',
  marginTop: '15px',
}));

interface EHRAdmitSelectionSectionProps {
  buttonText: string;
  titleText: string;
  onButtonClick: () => void;
}

const EHRAdmitSelectionSection = ({
  buttonText,
  titleText,
  onButtonClick,
}: EHRAdmitSelectionSectionProps) => {
  return (
    <ComponentContainer>
      <StyledText>{titleText}</StyledText>
      <ActionButton onClick={onButtonClick}>{buttonText}</ActionButton>
    </ComponentContainer>
  );
};

export default EHRAdmitSelectionSection;
