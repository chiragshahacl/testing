import { ThemeProvider } from '@mui/material';
import { fireEvent, render, screen } from '@testing-library/react';

import theme from '@/theme/theme';

import AddBedsContent from '@/components/modals/content/AddBedsContent';
import { MockBeds } from '@/utils/groupsMockData';
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

const MockErrors = {
  // eslint-disable-next-line camelcase
  bed_1: 'Please enter the bed ID.',
  // eslint-disable-next-line camelcase
  bed_2: 'Bed ID already exists. Change or enter a new one.',
};

const mockValidated = {
  bed_1: true, // eslint-disable-line camelcase
  bed_2: true, // eslint-disable-line camelcase
};

jest.mock('../src/utils/runtime', () => ({
  getCachedRuntimeConfig: () => ({
    MAX_NUMBER_BEDS: 64,
  }),
}));

describe('AddBedsContent', () => {
  /*
   * Requirement IDS: RQ-00022-B: SR-1.2.2.1, SR-1.2.2.12
   */
  it('renders all components', async () => {
    render(
      <ThemeProvider theme={theme}>
        <AddBedsContent
          beds={MockBeds}
          errors={MockErrors}
          validated={mockValidated}
          onAddBed={jest.fn()}
          onModifyBedNo={jest.fn()}
          onRemoveBed={jest.fn()}
          onClearError={jest.fn()}
        />
      </ThemeProvider>
    );

    expect(screen.getByText('Please enter the bed ID.')).toBeInTheDocument();
    expect(
      screen.getByText('Bed ID already exists. Change or enter a new one.')
    ).toBeInTheDocument();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.2.2.9
   */
  it('onRemoveBed called when bed removed', async () => {
    const onRemoveBedMock = jest.fn();

    render(
      <ThemeProvider theme={theme}>
        <AddBedsContent
          beds={MockBeds}
          errors={MockErrors}
          validated={mockValidated}
          onAddBed={jest.fn()}
          onModifyBedNo={jest.fn()}
          onRemoveBed={onRemoveBedMock}
          onClearError={jest.fn()}
        />
      </ThemeProvider>
    );

    expect(screen.getByText('Please enter the bed ID.')).toBeInTheDocument();
    fireEvent.click(screen.getByTestId('remove-bed-1'));
    expect(onRemoveBedMock).toHaveBeenCalledWith('bed_1');
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.2.1.3, SR-1.2.2.3, SR-1.2.2.15 RQ-00022-B: SR-1.2.2.11
   */
  it('onAddBed called when bed added', async () => {
    const onAddBedMock = jest.fn();

    render(
      <ThemeProvider theme={theme}>
        <AddBedsContent
          beds={MockBeds}
          errors={MockErrors}
          validated={mockValidated}
          onAddBed={onAddBedMock}
          onModifyBedNo={jest.fn()}
          onRemoveBed={jest.fn()}
          onClearError={jest.fn()}
        />
      </ThemeProvider>
    );

    fireEvent.click(screen.getByTestId('add-bed'));
    expect(onAddBedMock).toHaveBeenCalled();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.2.2.13 RQ-00022-B: SR-1.2.2.14
   */
  it('limits number of beds', async () => {
    render(
      <ThemeProvider theme={theme}>
        <AddBedsContent
          beds={[...MockBeds, ...MockBeds, ...MockBeds, ...MockBeds, ...MockBeds]}
          errors={{}}
          validated={mockValidated}
          onAddBed={jest.fn()}
          onModifyBedNo={jest.fn()}
          onRemoveBed={jest.fn()}
          onClearError={jest.fn()}
        />
      </ThemeProvider>
    );

    expect(screen.getByText('Step 1. Add beds to the system (80)')).toBeInTheDocument();
    fireEvent.click(screen.getByTestId('add-bed'));
    expect(screen.getByText('Bed limit reached')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Back to edit' }));
    expect(screen.queryByText('Bed limit reached')).not.toBeInTheDocument();
  });
});
