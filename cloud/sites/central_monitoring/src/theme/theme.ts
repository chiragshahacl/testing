import { createTheme } from '@mui/material/styles';
import components from './ComponentOverRide';
import shadows from './Shadows';
import typography from './Typography';

declare module '@mui/material/Typography' {
  interface TypographyPropsVariantOverrides {
    error: true;
    body3: true;
    bodySmall: true;
    metricNumberStyles: true;
  }
}

declare module '@mui/material/styles' {
  interface SimplePaletteColorOptions {
    secondary?: string;
  }

  interface TypeBackground {
    modal?: string;
    inactive?: string;
    active?: string;
    text?: string;
  }

  interface VitalsPaletteColor {
    green: string;
    lightGreen: string;
    blue: string;
    teal: string;
    default: string;
  }

  interface AlertPaletteColor {
    high: PaletteOptions['primary'];
    medium: string;
    low: string;
  }
  interface PaletteOptions {
    disabled: string;
    vitals: VitalsPaletteColor;
    alert: AlertPaletteColor;
  }
}

// Create a theme instance.
const theme = createTheme({
  spacing: 1,
  shape: {
    borderRadius: 1,
  },
  palette: {
    mode: 'dark',
    primary: {
      main: '#34B2EA',
      light: '#57C9FC',
      dark: '#0D151C',
    },
    secondary: {
      main: '#204160',
      light: '#1B98E3',
      dark: '#355464',
    },
    disabled: '#252829',
    divider: '#C1CEE2',
    background: {
      default: '#1C1C1E',
      modal: '#1A2630',
      inactive: '#5B6981',
      active: '#2188C6',
      text: '#010101',
    },
    vitals: {
      green: '#00C868',
      blue: '#57C4E8',
      lightGreen: '#CDE8C1',
      teal: '#21E5DF',
      default: '#C1CFE2',
    },
    success: {
      main: '#12FF8D',
      secondary: '#74E8EF',
    },
    error: {
      main: '#E95454',
      secondary: '#FF8585',
      dark: '#DE4038',
    },
    alert: {
      high: {
        main: '#FF4C42',
        light: '#FF7070',
      },
      medium: '#F6C905',
      low: '#75F8FC',
    },
    grey: {
      100: '#F3F5F6',
      200: '#C4C4C4',
      300: '#6B6B74',
      400: '#ffffff59',
      500: '#353537',
      600: '#F2F4F6',
      700: '#D0D3D7',
      800: '#A8ADB3',
      900: '#252c32',
    },
    common: {
      black: '#000000',
      white: '#FFFFFF',
    },
  },
  components,
  shadows,
  typography,
});

export default theme;
