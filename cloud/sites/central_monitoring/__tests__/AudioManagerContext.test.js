import { ALERT_AUDIO } from '@/constants';
import AudioManagerContext from '@/context/AudioManagerContext';
import SessionContext from '@/context/SessionContext';
import { STORAGE_KEYS } from '@/utils/storage';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { setupServer } from 'msw/node';
import { ALERT_PRIORITY } from '@/utils/metricCodes';
import TestComponent from '../__mocks__/AudioManagerContextChild';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 0,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
    },
  },
});

const server = setupServer();

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('AudioManagerContext', () => {
  it('setAudioAlert > high priority', async () => {
    jest
      .spyOn(window.HTMLMediaElement.prototype, 'play')
      .mockImplementation(() => Promise.resolve());
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <AudioManagerContext>
            <TestComponent />
          </AudioManagerContext>
        </SessionContext>
      </QueryClientProvider>
    );

    localStorage.setItem(
      STORAGE_KEYS.SCREEN_HANDLING_SOUND,
      JSON.stringify({ screen: 'this-screen' })
    );
    window.dispatchEvent(
      new StorageEvent('storage', {
        key: 'screenHandlingSound',
        newValue: JSON.stringify({ screen: 'this-screen' }),
      })
    );

    fireEvent.click(screen.getByRole('button', { name: 'setHighAudioAlert' }));
    await waitFor(() => {
      expect(screen.getByText(`currentAlertPriority: ${ALERT_PRIORITY.HIGH}`)).toBeInTheDocument();
    });
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.4.2.1
   */
  it('setAudioAlert > medium priority', async () => {
    jest
      .spyOn(window.HTMLMediaElement.prototype, 'play')
      .mockImplementation(() => Promise.resolve());

    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <AudioManagerContext>
            <TestComponent />
          </AudioManagerContext>
        </SessionContext>
      </QueryClientProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: 'setMedAudioAlert' }));
    await waitFor(() => {
      expect(
        screen.getByText(`currentAlertPriority: ${ALERT_PRIORITY.MEDIUM}`)
      ).toBeInTheDocument();
    });
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.4.2.1
   */
  it('setAudioAlert > low priority', async () => {
    jest
      .spyOn(window.HTMLMediaElement.prototype, 'play')
      .mockImplementation(() => Promise.resolve());

    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <AudioManagerContext>
            <TestComponent />
          </AudioManagerContext>
        </SessionContext>
      </QueryClientProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: 'setLowAudioAlert' }));
    await waitFor(() => {
      expect(screen.getByText(`currentAlertPriority: ${ALERT_PRIORITY.LOW}`)).toBeInTheDocument();
    });
  });

  it('audio pause event set to false', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <AudioManagerContext>
            <TestComponent />
          </AudioManagerContext>
        </SessionContext>
      </QueryClientProvider>
    );

    localStorage.setItem(STORAGE_KEYS.ALERT_AUDIO_PAUSED, 'false');
    window.dispatchEvent(
      new StorageEvent('storage', {
        key: 'alertAudioPause',
        newValue: 'false',
      })
    );
    await waitFor(() => {
      expect(screen.getByText('audioIsActive: false')).toBeInTheDocument();
    });
  });

  it('updateAudioSetting > audio on', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <AudioManagerContext>
            <TestComponent />
          </AudioManagerContext>
        </SessionContext>
      </QueryClientProvider>
    );

    localStorage.setItem(STORAGE_KEYS.ALERT_AUDIO_SETTING, ALERT_AUDIO.ON);
    fireEvent.click(screen.getByRole('button', { name: 'updateAudioSetting' }));
    window.dispatchEvent(
      new StorageEvent('storage', {
        key: STORAGE_KEYS.ALERT_AUDIO_SETTING,
        newValue: ALERT_AUDIO.ON,
      })
    );
    await waitFor(() => {
      expect(screen.getByText('audioAlarmSetting: audio_on')).toBeInTheDocument();
    });
  });

  it('updateAudioSetting > audio off', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <AudioManagerContext>
            <TestComponent />
          </AudioManagerContext>
        </SessionContext>
      </QueryClientProvider>
    );

    localStorage.setItem(STORAGE_KEYS.ALERT_AUDIO_SETTING, ALERT_AUDIO.OFF);
    fireEvent.click(screen.getByRole('button', { name: 'updateAudioSetting' }));
    window.dispatchEvent(
      new StorageEvent('storage', {
        key: STORAGE_KEYS.ALERT_AUDIO_SETTING,
        newValue: ALERT_AUDIO.OFF,
      })
    );
    await waitFor(() => {
      expect(screen.getByText('audioAlarmSetting: audio_off')).toBeInTheDocument();
    });
  });

  it('updateAudioSetting > pause audio', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <AudioManagerContext>
            <TestComponent />
          </AudioManagerContext>
        </SessionContext>
      </QueryClientProvider>
    );

    localStorage.setItem(STORAGE_KEYS.ALERT_AUDIO_PAUSED, 'false');
    window.dispatchEvent(
      new StorageEvent('storage', {
        key: 'alertAudioPause',
        newValue: 'false',
      })
    );
    await waitFor(() => {
      expect(screen.getByText('audioIsActive: false')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: 'updateAudioSetting' }));
    localStorage.setItem(STORAGE_KEYS.ALERT_AUDIO_SETTING, ALERT_AUDIO.ON);
    window.dispatchEvent(
      new StorageEvent('storage', {
        key: STORAGE_KEYS.ALERT_AUDIO_SETTING,
        newValue: ALERT_AUDIO.ON,
      })
    );
    await waitFor(() => {
      expect(screen.getByText('timerIsPaused: true')).toBeInTheDocument();
    });
  });

  it('setTriggerStopAudio', async () => {
    const mockSetItem = jest.spyOn(Storage.prototype, 'setItem');

    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <AudioManagerContext>
            <TestComponent />
          </AudioManagerContext>
        </SessionContext>
      </QueryClientProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: 'setActiveAlertsExist' }));
    await waitFor(() => {
      expect(screen.getByText('activeAlertsExist: true')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: 'setTriggerStopAudio' }));
    await waitFor(() => {
      expect(screen.getByText('activeAlertsExist: false')).toBeInTheDocument();
    });
  });

  it('updateAudioSetting > play audio', async () => {
    const mockAudio = jest
      .spyOn(window.HTMLMediaElement.prototype, 'play')
      .mockImplementation(() => Promise.resolve());

    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <AudioManagerContext>
            <TestComponent />
          </AudioManagerContext>
        </SessionContext>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('audioIsActive: true')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: 'setAutoPlayActivated' }));
    await waitFor(() => {
      expect(screen.getByText('autoPlayActivated: true')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: 'setHighAudioAlert' }));
    await waitFor(() => {
      expect(screen.getByText(`currentAlertPriority: ${ALERT_PRIORITY.HIGH}`)).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: 'setActiveAlertsExist' }));
    await waitFor(() => {
      expect(screen.getByText('activeAlertsExist: true')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: 'updateAudioSetting' }));
    localStorage.setItem(STORAGE_KEYS.ALERT_AUDIO_SETTING, ALERT_AUDIO.ON);
    window.dispatchEvent(
      new StorageEvent('storage', {
        key: STORAGE_KEYS.ALERT_AUDIO_SETTING,
        newValue: ALERT_AUDIO.ON,
      })
    );
    await waitFor(() => {
      expect(mockAudio).toHaveBeenCalled();
    });
  });

  it('audioIsActive when activeAlertsExist', async () => {
    const mockAudio = jest
      .spyOn(window.HTMLMediaElement.prototype, 'play')
      .mockImplementation(() => Promise.resolve());
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <AudioManagerContext>
            <TestComponent />
          </AudioManagerContext>
        </SessionContext>
      </QueryClientProvider>
    );

    localStorage.setItem(STORAGE_KEYS.ALERT_AUDIO_PAUSED, 'true');
    window.dispatchEvent(
      new StorageEvent('storage', {
        key: 'alertAudioPause',
        newValue: 'true',
      })
    );
    await waitFor(() => {
      expect(screen.getByText('audioIsActive: true')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: 'setAutoPlayActivated' }));
    await waitFor(() => {
      expect(screen.getByText('autoPlayActivated: true')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: 'setHighAudioAlert' }));
    await waitFor(() => {
      expect(screen.getByText(`currentAlertPriority: ${ALERT_PRIORITY.HIGH}`)).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: 'setActiveAlertsExist' }));
    await waitFor(() => {
      expect(screen.getByText('activeAlertsExist: true')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: 'setActiveAlertsExist' }));
    await waitFor(() => {
      expect(mockAudio).toHaveBeenCalled();
    });
  });
});
