import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import routeData from 'next/navigation';
import moment from 'moment';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { get } from 'lodash';

import TechnicalLogin from '@/app/technical/login/page';
import AudioManagerContext, { AudioManager } from '@/context/AudioManagerContext';
import RuntimeConfigProvider from '@/context/RuntimeContext';
import SessionContext from '@/context/SessionContext';
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

jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      replace: jest.fn(() => null),
    };
  },
}));

jest.mock('../src/utils/runtime', () => ({
  getCachedRuntimeConfig: () => ({
    APP_URL: 'https://api.dev.tucana.sibel.health',
    SIBEL_VERSION: 'v1.1',
  }),
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

const server = setupServer(
  rest.post('https://api.dev.tucana.sibel.health/web/auth/technical/token', (req, res, ctx) => {
    return res(
      ctx.json({
        access: 'access',
        refresh: 'refresh',
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Technical Login', () => {
  /*
   * Requirement IDs: RQ-00022-B: SR-1.1.3.1 RQ-00022-B: SR-1.8.1.16 RQ-00022-B: SR-1.1.3.1
   */
  it('renders all components', async () => {
    process.env.NEXT_PUBLIC_SIBEL_UDI = '(01)00860004541790(10)';

    render(
      <QueryClientProvider client={queryClient}>
        <RuntimeConfigProvider>
          <SessionContext>
            <AudioManagerContext>
              <TechnicalLogin />
            </AudioManagerContext>
          </SessionContext>
        </RuntimeConfigProvider>
      </QueryClientProvider>
    );

    expect(
      screen.getByRole('heading', {
        name: /Log in/i,
      })
    ).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Log in' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Log in' })).toBeDisabled();
    expect(screen.getByText('V1.1')).toBeInTheDocument();
    expect(
      screen.getByText(`Copyright © ${moment().year()} Sibel Inc. All rights reserved.`)
    ).toBeInTheDocument();
    expect(screen.getByText('UDI: (01)00860004541790(10)11')).toBeInTheDocument();
  });

  /*
   * Requriment IDs: RQ-00022-B: SR-1.1.1.3 RQ-00022-B: SR-1.1.1.2, SR-1.1.3.9 	RQ-00022-B: SR-1.1.1.3
   */
  it('handles too many attempts error', async () => {
    server.use(
      rest.post('https://api.dev.tucana.sibel.health/web/auth/technical/token', (req, res, ctx) => {
        return res(ctx.status(429));
      })
    );

    render(
      <QueryClientProvider client={queryClient}>
        <RuntimeConfigProvider>
          <SessionContext>
            <AudioManagerContext>
              <TechnicalLogin />
            </AudioManagerContext>
          </SessionContext>
        </RuntimeConfigProvider>
      </QueryClientProvider>
    );

    fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'password' } });
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Log in' })).not.toBeDisabled();
    });
    fireEvent.click(screen.getByRole('button', { name: 'Log in' }));
    await waitFor(() => {
      expect(
        screen.getByText('Too many attempts. Please try again in 15 minutes.')
      ).toBeInTheDocument();
    });
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.1.3.5
   */
  it('handles internal server error', async () => {
    server.use(
      rest.post('https://api.dev.tucana.sibel.health/web/auth/technical/token', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );
    render(
      <QueryClientProvider client={queryClient}>
        <RuntimeConfigProvider>
          <SessionContext>
            <AudioManagerContext>
              <TechnicalLogin />
            </AudioManagerContext>
          </SessionContext>
        </RuntimeConfigProvider>
      </QueryClientProvider>
    );

    fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'password' } });
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Log in' })).not.toBeDisabled();
    });
    fireEvent.click(screen.getByRole('button', { name: 'Log in' }));
    await waitFor(() => {
      expect(
        screen.getByText('Server error. Please try again in a few minutes.')
      ).toBeInTheDocument();
    });
  });

  it('handles other errors', async () => {
    server.use(
      rest.post('https://api.dev.tucana.sibel.health/web/auth/technical/token', (req, res, ctx) => {
        return res(ctx.status(401));
      })
    );

    render(
      <QueryClientProvider client={queryClient}>
        <RuntimeConfigProvider>
          <SessionContext>
            <AudioManagerContext>
              <TechnicalLogin />
            </AudioManagerContext>
          </SessionContext>
        </RuntimeConfigProvider>
      </QueryClientProvider>
    );

    fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'password' } });
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Log in' })).not.toBeDisabled();
    });
    fireEvent.click(screen.getByRole('button', { name: 'Log in' }));
    await waitFor(() => {
      expect(screen.getByText('Incorrect password. Please try again.')).toBeInTheDocument();
    });
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.1.3.2, SR-1.1.3.3, SR-1.1.3.12, SR-1.1.3.13, SR-1.2.1.1
   */
  it('redirects to home on successful login', async () => {
    const setAutoPlayActivatedMock = jest.fn();
    const replaceMock = jest.fn().mockImplementation(() => null);
    jest.spyOn(routeData, 'useRouter').mockImplementation(() => ({
      replace: replaceMock,
    }));
    render(
      <QueryClientProvider client={queryClient}>
        <RuntimeConfigProvider>
          <SessionContext>
            <AudioManager.Provider
              value={{
                setAutoPlayActivated: setAutoPlayActivatedMock,
              }}
            >
              <TechnicalLogin />
            </AudioManager.Provider>
          </SessionContext>
        </RuntimeConfigProvider>
      </QueryClientProvider>
    );

    fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'password' } });
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Log in' })).not.toBeDisabled();
    });
    fireEvent.click(screen.getByRole('button', { name: 'Log in' }));
    await waitFor(() => {
      expect(setAutoPlayActivatedMock).toHaveBeenCalledWith(true);
      expect(replaceMock).toHaveBeenCalledWith('/technical/home');
    });
  });
});
