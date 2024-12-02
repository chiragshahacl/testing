import { ThemeProvider } from '@mui/material';
import { fireEvent, render, screen } from '@testing-library/react';

import theme from '@/theme/theme';

import AlarmSettingUpdated from '@/components/modals/AlarmSettingUpdated';
import SessionContext from '@/context/SessionContext';

describe('AlarmSettingUpdated', () => {
  /*
   * Requirement IDs: RQ-00022-B: SR-1.1.6.9, SR-1.1.6.1, SR-1.1.6.13, SR-1.1.6.15, SR-1.1.6.16, SR-1.1.6.17, SR-1.1.6.18, SR-1.1.6.21
   */
  it('renders all components', async () => {
    const setOpenMock = jest.fn();

    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <AlarmSettingUpdated isOpen={true} onClose={setOpenMock} />
        </SessionContext>
      </ThemeProvider>
    );

    expect(screen.getByText('Alarm settings updated')).toBeInTheDocument();
    expect(screen.getByText('Alarm settings have been successfully updated.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Ok' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Ok' }));
    expect(setOpenMock).toHaveBeenCalled();
  });
});
