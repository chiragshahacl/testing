import { ThemeProvider } from '@mui/material';
import { render, screen } from '@testing-library/react';

import theme from '@/theme/theme';

import GraphInfo from '@/components/graph/GraphInfo';
import SessionContext from '@/context/SessionContext';
import { METRIC_INTERNAL_CODES } from '@/utils/metricCodes';

describe('GraphInfo', () => {
  it('renders all components', async () => {
    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <GraphInfo
            data={{
              bedNo: 'Bed 1',
              patient: {
                patientFirstName: 'John',
                patientLastName: 'Doe',
              },
            }}
            metric={METRIC_INTERNAL_CODES.ECG}
            hideText={false}
          />
        </SessionContext>
      </ThemeProvider>
    );

    expect(screen.getByText('Bed ID Bed 1')).toBeInTheDocument();
    expect(screen.getByText('Doe, J.')).toBeInTheDocument();
    expect(screen.getByText('ECG')).toBeInTheDocument();
  });
});
