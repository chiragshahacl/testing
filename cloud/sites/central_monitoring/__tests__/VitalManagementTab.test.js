import { ThemeProvider } from '@mui/material';
import { render, screen, waitFor } from '@testing-library/react';

import theme from '@/theme/theme';

import VitalManagementTab from '@/app/(authenticated)/home/details/Tabs/VitalsManagementTab';
import SessionContext from '@/context/SessionContext';

describe('VitalManagementTab', () => {
  it('renders all components', async () => {
    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <VitalManagementTab alertThresholds={{}} />
        </SessionContext>
      </ThemeProvider>
    );

    expect(screen.getByTestId('HR-bpm--?---?-')).toBeInTheDocument();
    expect(screen.getByTestId('SpO2-%--?---?-')).toBeInTheDocument();
    expect(screen.getByTestId('PR-bpm--?---?-')).toBeInTheDocument();
    expect(screen.getByTestId('RR-brpm--?---?-')).toBeInTheDocument();
    expect(screen.getByTestId('SYS-mmHg--?---?-')).toBeInTheDocument();
    expect(screen.getByTestId('DIA-mmHg--?---?-')).toBeInTheDocument();
    expect(screen.getByTestId('BODY TEMP-°F--?---?-')).toBeInTheDocument();
    expect(screen.getByTestId('SKIN TEMP-°F--?---?-')).toBeInTheDocument();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.3.2.1
   */
  it('renders custom limits', async () => {
    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <VitalManagementTab
            alertThresholds={{
              258418: {
                upperLimit: '120',
                lowerLimit: '45',
              },
              258419: {
                upperLimit: '30',
                lowerLimit: '5',
              },
              258421: {
                upperLimit: '160',
                lowerLimit: '90',
              },
              258422: {
                upperLimit: '110',
                lowerLimit: '50',
              },
              258420: {
                upperLimit: '100',
                lowerLimit: '85',
              },
              258427: {
                upperLimit: '120',
                lowerLimit: '45',
              },
              258424: {
                upperLimit: '102.2',
                lowerLimit: '93.2',
              },
              258425: {
                upperLimit: '102.2',
                lowerLimit: '93.2',
              },
            }}
          />
        </SessionContext>
      </ThemeProvider>
    );

    expect(screen.getByTestId('HR-bpm-120-45')).toBeInTheDocument();
    expect(screen.getByTestId('SpO2-%-100-85')).toBeInTheDocument();
    expect(screen.getByTestId('RR-brpm-30-5')).toBeInTheDocument();
    expect(screen.getByTestId('PR-bpm-120-45')).toBeInTheDocument();
    expect(screen.getByTestId('SYS-mmHg-160-90')).toBeInTheDocument();
    expect(screen.getByTestId('DIA-mmHg-110-50')).toBeInTheDocument();
    expect(screen.getByTestId('BODY TEMP-°F-102.2-93.2')).toBeInTheDocument();
    expect(screen.getByTestId('SKIN TEMP-°F-102.2-93.2')).toBeInTheDocument();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.3.1.1 RQ-00022-B: SR-1.3.8.1 RQ-00022-B: SR-1.3.5.32, SR-1.3.5.27 RQ-00022-B: SR-1.3.8.1 RQ-00022-B: SR-1.3.8.1 RQ-00022-B: SR-1.3.8.1 RQ-00022-B: SR-1.3.8.1 RQ-00022-B: SR-1.3.11.1 RQ-00022-B: SR-1.3.10.1
   * RQ-00022-B: SR-1.3.10.1
   */
  it('shows correct units', async () => {
    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <VitalManagementTab
            alertThresholds={{
              258418: {
                upperLimit: '120',
                lowerLimit: '45',
              },
              258419: {
                upperLimit: '30',
                lowerLimit: '5',
              },
              258421: {
                upperLimit: '160',
                lowerLimit: '90',
              },
              258422: {
                upperLimit: '110',
                lowerLimit: '50',
              },
              258420: {
                upperLimit: '100',
                lowerLimit: '85',
              },
              258427: {
                upperLimit: '120',
                lowerLimit: '45',
              },
              258424: {
                upperLimit: '102.2',
                lowerLimit: '93.2',
              },
            }}
            metrics={{
              hr: { value: undefined, unit: 'bpm' },
              spo2: { value: undefined, unit: '%' },
              rrMetric: { value: undefined, unit: 'brpm' },
              pr: { value: undefined, unit: 'bpm' },
              dia: { value: undefined, unit: 'mmHg' },
              sys: { value: undefined, unit: 'mmHg' },
              bodyTemp: { value: undefined, unit: '°F' },
              limbTemp: { value: undefined, unit: '°F' },
              chestTemp: { value: undefined, unit: '°F' },
            }}
          />
        </SessionContext>
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getAllByText('bpm')).toHaveLength(2);
      expect(screen.getByText('%')).toBeInTheDocument();
      expect(screen.getByText('brpm')).toBeInTheDocument();
      expect(screen.getAllByText('°F')).toHaveLength(2);
      expect(screen.getAllByText('mmHg')).toHaveLength(2);
    });
  });
});
