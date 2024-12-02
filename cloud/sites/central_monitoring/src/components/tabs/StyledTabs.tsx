import { openSansFont } from '@/utils/fonts';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import Typography from '@mui/material/Typography';
import { styled } from '@mui/material/styles';

interface StyledTabProps {
  label: string;
  value: string;
}

export const StyledTab = styled((props: StyledTabProps) => <Tab disableRipple {...props} />)(
  ({ theme }) => ({
    color: theme.palette.common.white,
    fontWeight: 400,
    fontSize: 18,
    lineHeight: '24px',
    display: 'flex',
    alignItems: 'center',
    textAlign: 'center',
    width: '20%',
    height: 0,
  })
);

interface StyledTabsProps {
  children?: React.ReactNode;
  value: string;
  label: string;
  onChange: (event: React.SyntheticEvent, newValue: string) => void;
}

export const StyledPatientInfoText = styled(Typography, {
  shouldForwardProp: (prop) => prop !== 'bold',
})<{ bold?: boolean }>(({ bold }) => ({
  fontFamily: openSansFont.style.fontFamily,
  fontWeight: bold ? 600 : 400,
  alignItems: 'center',
  textAlign: 'center',
  lineHeight: '22px',
}));

export const StyledTabs = styled((props: StyledTabsProps) => <Tabs {...props} />)(
  ({ theme, label }) => ({
    '& .Mui-selected': {
      backgroundColor: `${theme.palette.secondary.main} !important`,
      fontWeight: 700,
      color: `${theme.palette.primary.dark} !important`,
      '&::before': {
        backgroundColor: `${theme.palette.primary.light} !important`,
        borderRadius: `${theme.spacing(8, 8, 0, 0)} !important`,
        content: `"${label}"`,
        alignItems: 'center',
        justifyContent: 'center',
        display: 'flex',
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
      },
    },
    '& .MuiTabs-indicator': {
      display: 'flex',
      justifyContent: 'center',
      backgroundColor: 'transparent',
    },
    '& .MuiTab-root': {
      backgroundColor: theme.palette.secondary.main,
    },
    '& :first-of-type': {
      borderRadius: theme.spacing(8, 0, 0, 0),
    },
    '& :last-child': {
      borderRadius: theme.spacing(0, 8, 0, 0),
    },
  })
);
