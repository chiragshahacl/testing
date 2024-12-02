import { ThemeProvider } from '@mui/material';
import { render, screen } from '@testing-library/react';

import theme from '@/theme/theme';

import NoDataBed from '@/components/graph/NoDataBed';
import SessionContext from '@/context/SessionContext';

describe('NoDataBed', () => {
  it('renders all components', async () => {
    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <NoDataBed bedNo='Bed 1' showSettings={true} />
        </SessionContext>
      </ThemeProvider>
    );

    expect(screen.getByText('Bed ID Bed 1')).toBeInTheDocument();
    expect(screen.getByText('PATIENT MONITOR IS NOT AVAILABLE')).toBeInTheDocument();
  });
});
