import { ThemeProvider } from '@mui/material';
import { render, screen } from '@testing-library/react';

import theme from '@/theme/theme';

import GraphSummary from '@/components/graph/GraphSummary';
import SessionContext from '@/context/SessionContext';
import { truncate } from 'lodash';

describe('GraphSummary', () => {
  it('renders all components', async () => {
    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <GraphSummary
            data={{
              lowLimit: 80,
              highLimit: 120,
              hr: 100,
            }}
          />
        </SessionContext>
      </ThemeProvider>
    );

    expect(screen.getByText('HR (bpm)')).toBeInTheDocument();
    expect(screen.getByText('80')).toBeInTheDocument();
    expect(screen.getByText('120')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument();
  });

  it('renders small view', async () => {
    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <GraphSummary
            data={{
              lowLimit: 80,
              highLimit: 120,
              hr: 100,
            }}
            smallView={truncate}
          />
        </SessionContext>
      </ThemeProvider>
    );

    expect(screen.getByTestId('graph-summary')).toHaveStyle({ height: '18px' });
  });
});
