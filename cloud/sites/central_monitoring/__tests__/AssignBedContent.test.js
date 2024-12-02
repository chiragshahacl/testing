import { ThemeProvider } from '@mui/material';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import theme from '@/theme/theme';

import AssignBedContent from '@/components/modals/content/AssignBedContent';
import SessionContext from '@/context/SessionContext';
import { get } from 'lodash';
import { translationFile } from '@/utils/translation';

const mockTranslationFile = translationFile;
const mockLodashGet = get;

jest.mock('react-i18next', () => ({
  useTranslation: () => {
    return {
      t: (key, replaceValues) => {
        let translatedText = mockLodashGet(mockTranslationFile['en']['translation'], key, '');
        if (replaceValues && translatedText) {
          Object.entries(replaceValues).forEach(([key, value]) => {
            translatedText = translatedText.replaceAll(`{{${key}}}`, value);
          });
        }
        return translatedText || key;
      },
    };
  },
}));

describe('AssignBedContent', () => {
  /*
   * Requirement IDs: RQ-00022-B: SR-1.2.3.12
   */
  it('renders all components', async () => {
    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <AssignBedContent
            beds={[]}
            patientMonitors={[]}
            onAdd={jest.fn()}
            serverError={null}
            isLoading
          />
        </SessionContext>
      </ThemeProvider>
    );

    expect(screen.getByText('Step 2. Assign patient monitors to beds')).toBeInTheDocument();
    expect(screen.getByText('Select the bed ID in the second column.')).toBeInTheDocument();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.8.1.10, SR-1.8.1.11, SR-1.8.1.12, SR-1.8.1.13 RQ-00022-B: SR-1.8.1.2
   */
  it('renders monitor IDs', async () => {
    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <AssignBedContent
            beds={[]}
            patientMonitors={[
              {
                id: '001',
                monitorId: 'm-001',
                assignedBedId: 'N/A',
              },
            ]}
            onAdd={jest.fn()}
          />
        </SessionContext>
      </ThemeProvider>
    );

    expect(screen.getByText('m-001')).toBeInTheDocument();
    expect(screen.getByText('N/A')).toBeInTheDocument();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.2.1.3, SR-1.2.3.3, SR-1.2.3.9, SR-1.2.3.10, SR-1.2.3.13, SR-1.2.3.21 	RQ-00022-B: SR-1.2.3.15
   */
  it('shows beds no in dropdown', async () => {
    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <AssignBedContent
            beds={[
              {
                id: 'b-001',
                monitorId: '',
                bedNo: '1',
                patient: {
                  patientId: 'p-001',
                  patientPrimaryIdentifier: 'pid1',
                  patientFirstName: 'John',
                  patientLastName: 'Doe',
                  patientGender: 'male',
                  patientDob: '01-01-1990',
                },
              },
              {
                id: 'b-002',
                monitorId: '',
                bedNo: '2',
                patient: {
                  patientId: 'p-002',
                  patientPrimaryIdentifier: 'pid2',
                  patientFirstName: 'John',
                  patientLastName: 'Doe',
                  patientGender: 'male',
                  patientDob: '01-01-1990',
                },
              },
            ]}
            patientMonitors={[
              {
                id: '001',
                monitorId: 'm-001',
                assignedBedId: 'N/A',
              },
            ]}
            onAdd={jest.fn()}
          />
        </SessionContext>
      </ThemeProvider>
    );

    fireEvent.mouseDown(screen.getAllByRole('combobox')[0]);
    await waitFor(() => {
      expect(screen.getByText('1')).toBeInTheDocument();
      expect(screen.getByText('2')).toBeInTheDocument();
    });
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.2.3.17
   */
  it('saves assigned beds', async () => {
    const setPatientMonitorsMock = jest.fn();

    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <AssignBedContent
            beds={[
              {
                id: 'b-001',
                monitorId: '',
                bedNo: '1',
                patient: {
                  patientId: 'p-001',
                  patientPrimaryIdentifier: 'pid1',
                  patientFirstName: 'John',
                  patientLastName: 'Doe',
                  patientGender: 'male',
                  patientDob: '01-01-1990',
                },
              },
              {
                id: 'b-002',
                monitorId: '',
                bedNo: '2',
                patient: {
                  patientId: 'p-002',
                  patientPrimaryIdentifier: 'pid2',
                  patientFirstName: 'John',
                  patientLastName: 'Doe',
                  patientGender: 'male',
                  patientDob: '01-01-1990',
                },
              },
            ]}
            patientMonitors={[
              {
                id: '001',
                monitorId: 'm-001',
                assignedBedId: 'N/A',
              },
            ]}
            onAdd={setPatientMonitorsMock}
          />
        </SessionContext>
      </ThemeProvider>
    );

    fireEvent.mouseDown(screen.getByRole('combobox'));
    fireEvent.click(screen.getByRole('option', { name: '1' }));
    await waitFor(() => {
      expect(setPatientMonitorsMock).toHaveBeenCalledWith([
        {
          id: '001',
          monitorId: 'm-001',
          assignedBedId: 'b-001',
        },
      ]);
    });
  });
});
