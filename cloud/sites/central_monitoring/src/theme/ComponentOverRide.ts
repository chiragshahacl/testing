const components = {
  MuiCssBaseline: {
    styleOverrides: {
      '*': {
        boxSizing: 'border-box',
      },
      html: {
        height: '100%',
        width: '100%',
      },
      body: {
        height: '100%',
        margin: 0,
        padding: 0,
      },
      '#root': {
        height: '100%',
      },
      '.scrollbar-container': {
        borderRight: '0 !important',
      },
      '.radial-gradient': {
        position: 'absolute',
        left: 0,
        right: 0,
        top: 0,
        bottom: 0,
        background:
          'radial-gradient(50% 62.35% at 65.63% 39.24%, rgba(50, 165, 216, 0.63) 0%, rgba(163, 157, 107, 0) 100%);',
        minHeight: '100vh',
      },
      '.border-gradient': {
        padding: '32px',
        width: '552px',
        background: 'transparent',
        backdropFilter: 'blur(53.1795px)',
        borderRadius: '16px',
      },
      '.topbar-border': {
        height: '6px',
        background:
          'linear-gradient(90deg, rgba(52, 178, 234, 0) 0%, #102033 0%, #2C97C7 46.35%, #34B2EA 100%)',
      },
      '.unselected': {
        backgroundColor: '#5B6981 !important',
        color: '#C4C4C4 !important',
        fontWeight: '400 !important',
      },
      '.container .column:first-of-type:nth-last-of-type(-n+16), .container  .column:first-of-type:nth-last-of-type(-n+16) ~ .column':
        {
          height: 'calc(12.5% - 6px)',
        },
      '.container .column:first-of-type:nth-last-of-type(-n+8), .container  .column:first-of-type:nth-last-of-type(-n+8) ~ .column':
        {
          height: 'calc(25% - 5px)',
        },
      '.container .column:first-of-type:nth-last-of-type(-n+4), .container  .column:first-of-type:nth-last-of-type(-n+4) ~ .column':
        {
          height: 'calc(50% - 3px)',
        },
      '.container .column:first-of-type:nth-last-of-type(-n+2), .container  .column:first-of-type:nth-last-of-type(-n+2) ~ .column':
        {
          flex: 1,
          width: '100%',
        },
      '.container': {
        display: 'flex',
        flexWrap: 'wrap',
        height: 'calc(100vh - 100px)',
        gap: '6px',
        padding: '6px',
        flexDirection: 'column',
      },
      '.container .column': {
        display: 'flex',
        flexDirection: 'column',
      },
      '.metricCard': {
        display: 'flex',
        flex: 1,
        padding: '8px',
        backgroundColor: '#0D151C',
        borderRadius: '8px',
        justifyContent: 'space-between',
      },
      '.metricCardTopValue.metricCardWithAlert, .metricCardMiddleValue.metricCardWithAlert': {
        borderRadius: '8px',
        padding: '8px',
      },
      '.metricCardTopValue.metricCardWithAlert': {
        margin: '-8px -8px 0px -8px',
      },
      '.metricCardMiddleValue.metricCardWithAlert': {
        margin: '0px -8px 0px -8px',
      },
      '.metricCardTopValue': {
        display: 'flex',
        flex: 1,
        justifyContent: 'space-between',
      },
      '.metricCardMiddleValue': {
        display: 'flex',
        flex: 1,
        justifyContent: 'space-between',
      },
      '.metricCardBottomValue': {
        display: 'flex',
        flex: 1,
        justifyContent: 'space-between',
      },
      '.metricCardWithLowAlert': {
        backgroundColor: '#75F8FC',
      },
      '.metricCardWithMedAlert': {
        backgroundColor: '#F6C905',
        animation: 'med-flash 1.67s infinite',
      },
      '@keyframes med-flash': {
        '0%, 25%': {
          opacity: 0.75,
        },
        '12.5%, 37.5%': {
          opacity: 1,
        },
      },
      '.metricCardWithHighAlert': {
        backgroundColor: '#FF4C42',
        animation: 'high-flash 0.476s infinite',
      },
      '@keyframes high-flash': {
        '0%, 12.5%': {
          opacity: 0.75,
        },
        '6.25%, 18.75%': {
          opacity: 1,
        },
      },
      '.bedCard': {
        borderRadius: '18px',
        width: '100%',
        maxWidth: '220px',
        position: 'relative',
        height: 'calc((90vh - 80px) / 8)',
        minHeight: '100px',
        justifyContent: 'space-between',
        display: 'flex',
        flexDirection: 'column !important',
      },
      '.ehrDatePicker fieldset': {
        border: 'none !important',
      },
    },
  },

  MuiContainer: {
    styleOverrides: {
      root: {
        paddingLeft: '12px !important',
        paddingRight: '12px !important',
        maxWidth: '1600px',
      },
    },
  },

  MuiOutlinedInput: {
    styleOverrides: {
      input: {
        overflow: 'hidden',
        textOverflow: 'ellipsis',
      },
      root: {
        borderRadius: '16px',
        color: '#F2F4F6',
        marginY: '12px',
        '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
          border: '1px solid #F2F4F6',
        },
        '&.Mui-error .MuiOutlinedInput-notchedOutline': {
          border: '1px solid #FF4C42',
        },
      },
    },
  },

  MuiButton: {
    styleOverrides: {
      outlined: {
        height: '48px',
        padding: '8px 22px',
        backgroundColor: 'transparent',
        borderRadius: '64px',
        border: '1px solid #F2F4F6',
        color: '#F2F4F6',
        '&:hover': {
          backgroundColor: 'transparent',
          border: '1px solid #F2F4F6',
        },
      },
      contained: {
        height: '48px',
        padding: '8px 22px',
        backgroundColor: '#2188C6',
        borderRadius: '64px',
        color: '#FFFFFF',
        '&:hover': {
          backgroundColor: '#2188C6',
        },
        '&.Mui-disabled': {
          backgroundColor: '#252829',
          color: '#5C5C5C',
        },
      },
      sizeSmall: {
        height: '36px',
        padding: '8px 16px',
        borderRadius: '16px',
        fontSize: '17px',
        fontWeight: '700',
        lineHeight: '20px',
        margin: '0px 7.5px',
        color: '#000000',
      },
      text: {
        color: '#FFFFFF',
        borderRadius: 0,
        '&:hover': {
          backgroundColor: '#1A2630',
        },
      },
    },
  },

  MuiMenuItem: {
    styleOverrides: {
      root: {
        '&.Mui-selected': {
          backgroundColor: '#1A5F89 !important',
        },
        '&.Mui-disabled': {
          opacity: 1,
          color: 'rgba(255, 255, 255, 0.5)',
        },
      },
    },
  },

  MuiTableCell: {
    styleOverrides: {
      root: {
        borderBottom: 'none',
      },
    },
  },

  MuiCircularProgress: {
    styleOverrides: {
      colorPrimary: {
        color: '#C4C4C4',
      },
    },
  },
};

export default components;
