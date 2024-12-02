import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import ManageAudioAlert from '@/components/Settings/ManageAudioAlert';
import { ALERT_AUDIO } from '@/constants';
import { AudioManager } from '@/context/AudioManagerContext';
import SessionContext from '@/context/SessionContext';

import { rest } from 'msw';
import { setupServer } from 'msw/node';

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
  rest.post('/web/auth/token', (req, res, ctx) => {
    return res(ctx.status(200));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('ManageAudioAlertModal', () => {
  const onSetOpenMock = jest.fn();
  const setAutoPlayActivatedMock = jest.fn();

  it('renders all components', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <AudioManager.Provider
            value={{
              audioAlarmSetting: ALERT_AUDIO.ON,
              audioIsActive: true,
              autoPlayActivated: false,
              setAutoPlayActivated: setAutoPlayActivatedMock,
            }}
          >
            <ManageAudioAlert isOpen={true} onSetOpen={onSetOpenMock} />
          </AudioManager.Provider>
        </SessionContext>
      </QueryClientProvider>
    );

    expect(screen.getByTestId('dismiss-modal')).toBeInTheDocument();
    expect(screen.getByTestId('audio_on')).toBeInTheDocument();
    expect(screen.getByText('Manage audio alarm')).toBeInTheDocument();
    expect(screen.getByText('OFF')).toBeInTheDocument();
    expect(screen.getByText('ON')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Save' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Save' })).toBeDisabled();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.1.6.9, SR-1.1.6.1, SR-1.1.6.13, SR-1.1.6.15, SR-1.1.6.16, SR-1.1.6.17, SR-1.1.6.19, SR-1.1.6.21
   * RQ-00022-B: SR-1.1.6.8, SR-1.1.6.1, SR-1.1.6.13, SR-1.1.6.15, SR-1.1.6.16, SR-1.1.6.17, SR-1.1.6.19, SR-1.1.6.21, SR-1.1.6.22
   */
  it('updates settings from ON to OFF', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <AudioManager.Provider
            value={{
              audioAlarmSetting: ALERT_AUDIO.ON,
              audioIsActive: true,
              autoPlayActivated: false,
              setAutoPlayActivated: setAutoPlayActivatedMock,
            }}
          >
            <ManageAudioAlert isOpen={true} onSetOpen={onSetOpenMock} />
          </AudioManager.Provider>
        </SessionContext>
      </QueryClientProvider>
    );

    expect(screen.getByTestId('audio_on')).toBeInTheDocument();
    fireEvent.click(screen.getByTestId('audio_on'));
    await waitFor(() => {
      expect(screen.getByTestId('audio_off')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Save' })).not.toBeDisabled();
    });
  });

  it('updates settings from OFF to ON', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <AudioManager.Provider
            value={{
              audioAlarmSetting: ALERT_AUDIO.OFF,
              audioIsActive: true,
              autoPlayActivated: false,
              setAutoPlayActivated: setAutoPlayActivatedMock,
            }}
          >
            <ManageAudioAlert isOpen={true} onSetOpen={onSetOpenMock} />
          </AudioManager.Provider>
        </SessionContext>
      </QueryClientProvider>
    );

    expect(screen.getByTestId('audio_off')).toBeInTheDocument();
    fireEvent.click(screen.getByTestId('audio_off'));
    expect(screen.getByTestId('audio_on')).toBeInTheDocument();
  });

  it('back to edit', async () => {
    server.use(
      rest.post('/web/auth/token', (req, res, ctx) => {
        return res(
          ctx.status(200),
          ctx.json({
            access: 'access',
            refresh: 'refresh',
          })
        );
      })
    );
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <AudioManager.Provider
            value={{
              audioAlarmSetting: ALERT_AUDIO.OFF,
              audioIsActive: true,
              autoPlayActivated: false,
              setAutoPlayActivated: setAutoPlayActivatedMock,
            }}
          >
            <ManageAudioAlert isOpen={true} onSetOpen={onSetOpenMock} />
          </AudioManager.Provider>
        </SessionContext>
      </QueryClientProvider>
    );

    fireEvent.click(screen.getByTestId('audio_off'));
    fireEvent.click(screen.getByTestId('save-button'));

    await waitFor(() => {
      expect(screen.getByTestId('back-to-edit-button')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('back-to-edit-button'));

    await waitFor(() => {
      expect(screen.getByText('Manage audio alarm')).toBeInTheDocument();
    });
  });

  /*
   * Requirment IDs: RQ-00022-B: SR-1.1.6.20
   */
  it('submits new value', async () => {
    server.use(
      rest.post('/web/auth/token', (req, res, ctx) => {
        return res(
          ctx.status(200),
          ctx.json({
            access: 'access',
            refresh: 'refresh',
          })
        );
      })
    );
    const mockSetItem = jest.spyOn(Storage.prototype, 'setItem');
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <AudioManager.Provider
            value={{
              audioAlarmSetting: ALERT_AUDIO.OFF,
              audioIsActive: true,
              autoPlayActivated: false,
              setAutoPlayActivated: setAutoPlayActivatedMock,
            }}
          >
            <ManageAudioAlert isOpen={true} onSetOpen={onSetOpenMock} />
          </AudioManager.Provider>
        </SessionContext>
      </QueryClientProvider>
    );

    fireEvent.click(screen.getByTestId('audio_off'));
    fireEvent.click(screen.getByTestId('save-button'));

    await waitFor(() => {
      expect(screen.getByText('Password required')).toBeInTheDocument();
    });
    const passwordInput = screen.getByPlaceholderText('Password');

    fireEvent.change(passwordInput, {
      target: { value: 'password' },
    });
    await waitFor(() => {
      expect(screen.getByTestId('submit-button')).not.toBeDisabled();
    });
    fireEvent.click(screen.getByTestId('submit-button'));
    await waitFor(() => {
      expect(screen.getByText('Alarm settings updated')).toBeInTheDocument();
      expect(
        screen.getByText('Alarm settings have been successfully updated.')
      ).toBeInTheDocument();
      expect(mockSetItem).toHaveBeenCalledWith('alertAudioSetting', 'audio_on');
    });
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.1.6.14
   */
  it('handles close', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <AudioManager.Provider
            value={{
              audioAlarmSetting: ALERT_AUDIO.ON,
              audioIsActive: true,
              autoPlayActivated: false,
              setAutoPlayActivated: setAutoPlayActivatedMock,
            }}
          >
            <ManageAudioAlert isOpen={true} onSetOpen={onSetOpenMock} />
          </AudioManager.Provider>
        </SessionContext>
      </QueryClientProvider>
    );

    fireEvent.click(screen.getByTestId('dismiss-modal'));
    await waitFor(() => {
      expect(onSetOpenMock).toHaveBeenCalledWith(false);
    });
  });

  it('checks unsaved changes', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <AudioManager.Provider
            value={{
              audioAlarmSetting: ALERT_AUDIO.ON,
              audioIsActive: true,
              autoPlayActivated: false,
              setAutoPlayActivated: setAutoPlayActivatedMock,
            }}
          >
            <ManageAudioAlert isOpen={true} onSetOpen={onSetOpenMock} />
          </AudioManager.Provider>
        </SessionContext>
      </QueryClientProvider>
    );

    expect(screen.getByTestId('audio_on')).toBeInTheDocument();
    fireEvent.click(screen.getByTestId('audio_on'));
    fireEvent.click(screen.getByTestId('dismiss-modal'));
    await waitFor(() => {
      expect(screen.getByText('Unsaved changes')).toBeInTheDocument();
    });
  });
});
