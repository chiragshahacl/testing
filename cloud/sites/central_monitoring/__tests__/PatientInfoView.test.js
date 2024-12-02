import { ThemeProvider } from '@mui/material';
import { render, screen } from '@testing-library/react';
import moment from 'moment';

import theme from '@/theme/theme';

import PatientInfoTab from '@/app/(authenticated)/home/details/Tabs/PatientInformationTab';
import SessionContext from '@/context/SessionContext';

describe('PatientInfoTab', () => {
  /*
   * Requirement IDs: RQ-00022-B: SR-1.5.1.5, SR-1.5.1.7 RQ-00022-B: SR-1.8.1.25, SR-1.5.1.3
   */
  it('renders all components', async () => {
    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <PatientInfoTab
            id='id'
            firstName='John'
            lastName='Doe'
            sex='Male'
            dob={moment('01/01/1997').format('yyyy-MM-DD')}
          />
        </SessionContext>
      </ThemeProvider>
    );

    expect(screen.getByText('Demographic info')).toBeInTheDocument();
    expect(screen.getByText('ID')).toBeInTheDocument();
    expect(screen.getByText('id')).toBeInTheDocument();
    expect(screen.getByText('First name')).toBeInTheDocument();
    expect(screen.getByText('John')).toBeInTheDocument();
    expect(screen.getByText('Last name')).toBeInTheDocument();
    expect(screen.getByText('Doe')).toBeInTheDocument();
    expect(screen.getByText('Sex')).toBeInTheDocument();
    expect(screen.getByText('Male')).toBeInTheDocument();
    expect(screen.getByText('DOB')).toBeInTheDocument();
    expect(screen.getByText('1997-01-01')).toBeInTheDocument();
  });
});
