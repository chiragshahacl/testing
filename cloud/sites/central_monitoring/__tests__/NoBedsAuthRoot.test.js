import theme from '@/theme/theme';
import { ThemeProvider } from '@mui/material';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import RootLayout from '@/app/(authenticated)/layout';
import { ALERT_AUDIO } from '@/constants';
import { STORAGE_KEYS } from '@/utils/storage';
import AudioManagerContext, { AudioManager } from '@/context/AudioManagerContext';
import PatientsContext from '@/context/PatientsContext';
import SessionContext from '@/context/SessionContext';
import { MockGroups, MockPatientMonitors } from '@/utils/groupsMockData';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
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

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 0,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
    },
  },
});

jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      replace: jest.fn(() => null),
    };
  },
  useSearchParams() {
    return undefined;
  },
}));

describe('no beds in system', () => {
  const server = setupServer(
    rest.post('/web/auth/token', (req, res, ctx) => {
      return res(
        ctx.json({
          access: 'access',
          refresh: 'refresh',
        })
      );
    }),
    rest.get('/web/device', (req, res, ctx) => {
      return res(
        ctx.json({
          resources: MockPatientMonitors,
        })
      );
    }),
    rest.get('/web/bed', (req, res, ctx) => {
      return res(
        ctx.json({
          resources: [],
        })
      );
    }),
    rest.get('/web/bed-group', (req, res, ctx) => {
      return res(
        ctx.json({
          resources: MockGroups,
        })
      );
    })
  );

  beforeAll(() => {
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, 'accessToken');
    localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, 'refreshToken');
    localStorage.setItem(STORAGE_KEYS.USER_TYPE, 'non-technical');
    server.listen();
  });
  afterAll(() => server.close());

  /*
   * Requirement IDs: RQ-00022-B: SR-1.2.1.1
   */
  it('shows bed management modal when open', async () => {
    render(
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <SessionContext>
            <AudioManagerContext>
              <PatientsContext>
                <RootLayout>
                  <div data-testid='child' />
                </RootLayout>
              </PatientsContext>
            </AudioManagerContext>
          </SessionContext>
        </QueryClientProvider>
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('Bed Management-modal')).toBeInTheDocument();
      expect(screen.queryByTestId('Group Management-modal')).not.toBeInTheDocument();
    });
  });

  it('hides bed management modal on user action', async () => {
    const setAutoPlayActivatedMock = jest.fn();

    render(
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <SessionContext>
            <AudioManager.Provider
              value={{
                audioAlarmSetting: ALERT_AUDIO.ON,
                audioIsActive: true,
                autoPlayActivated: false,
                setAutoPlayActivated: setAutoPlayActivatedMock,
                setTimerIsPaused: jest.fn(),
                setAudioDisabledTimer: jest.fn(),
              }}
            >
              <PatientsContext>
                <RootLayout>
                  <div data-testid='child' />
                </RootLayout>
              </PatientsContext>
            </AudioManager.Provider>
          </SessionContext>
        </QueryClientProvider>
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('Bed Management-modal')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('dismiss-modal'));
    await waitFor(() => {
      expect(setAutoPlayActivatedMock).toHaveBeenCalledWith(true);
    });
  });
});
