import NetworkManager from '@/components/network/NetworkManager';

import { AudioManager } from '@/context/AudioManagerContext';
import SessionContext from '@/context/SessionContext';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';

let mockIsOnline = true;
jest.mock('@/hooks/useNetwork', () => {
  return jest.fn(() => mockIsOnline);
});

let mockServerIsOnline = true;
jest.mock('@/api/useHealthcheck', () => {
  return { useHealthcheck: jest.fn(() => mockServerIsOnline) };
});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 0,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
    },
  },
});

describe('Network manager modal', () => {
  /*
   * Requirement IDs: RQ-00022-B: SR-1.8.2.1, SR-1.3.15.92
   */
  it('Displays network disconnected modal', async () => {
    mockIsOnline = false;
    const { rerender } = render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            setAudioAlert: jest.fn(),
            setActiveAlertsExist: jest.fn(),
          }}
        >
          <SessionContext>
            <NetworkManager />
          </SessionContext>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    const title = screen.getByText('Network disconnected');
    const description = screen.getByText(
      'Unable to detect a network connection. Please check your network settings. If the problem persists, contact support.'
    );
    const button = screen.getByRole('button', { name: 'Ok' });

    expect(title).toBeInTheDocument();
    expect(description).toBeInTheDocument();
    expect(button).toBeInTheDocument();

    mockIsOnline = true;
    rerender(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            setAudioAlert: jest.fn(),
            setActiveAlertsExist: jest.fn(),
          }}
        >
          <SessionContext>
            <NetworkManager />
          </SessionContext>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    expect(title).toBeInTheDocument();
    expect(description).toBeInTheDocument();
    expect(button).toBeInTheDocument();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.3.15.93
   */
  it('Displays server disconnected modal', async () => {
    mockServerIsOnline = false;
    const { rerender } = render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            setAudioAlert: jest.fn(),
            setActiveAlertsExist: jest.fn(),
          }}
        >
          <SessionContext>
            <NetworkManager />
          </SessionContext>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    const title = screen.getByText('Something went wrong');
    const description = screen.getByText(
      'The system has detected an error during operation. If the problem persists, contact support and restart the central server.'
    );
    const button = screen.getByRole('button', { name: 'Ok' });

    expect(title).toBeInTheDocument();
    expect(description).toBeInTheDocument();
    expect(button).toBeInTheDocument();

    mockServerIsOnline = true;
    rerender(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            setAudioAlert: jest.fn(),
            setActiveAlertsExist: jest.fn(),
          }}
        >
          <SessionContext>
            <NetworkManager />
          </SessionContext>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    expect(title).toBeInTheDocument();
    expect(description).toBeInTheDocument();
    expect(button).toBeInTheDocument();
  });

  it('Triggers audio alert when connection lost', async () => {
    mockIsOnline = false;
    const setAudioAlert = jest.fn();
    const setActiveAlertsExist = jest.fn();
    render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            setAudioAlert,
            setActiveAlertsExist,
          }}
        >
          <SessionContext>
            <NetworkManager />
          </SessionContext>
        </AudioManager.Provider>
      </QueryClientProvider>
    );
    expect(setAudioAlert).toBeCalledWith(
      [expect.objectContaining({ id: 'network-error-alert' })],
      true
    );
    expect(setActiveAlertsExist).toBeCalledWith(true);
  });

  it('Stops audio alert when connection restored and user confirms', async () => {
    mockIsOnline = false;
    const setTriggerStopAudio = jest.fn();

    const { rerender } = render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            setAudioAlert: jest.fn(),
            setActiveAlertsExist: jest.fn(),
            setTriggerStopAudio,
          }}
        >
          <SessionContext>
            <NetworkManager />
          </SessionContext>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    mockIsOnline = true;

    rerender(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            setTriggerStopAudio,
          }}
        >
          <SessionContext>
            <NetworkManager />
          </SessionContext>
        </AudioManager.Provider>
      </QueryClientProvider>
    );
    const button = screen.getByRole('button', { name: 'Ok' });
    expect(button).toBeInTheDocument();
    fireEvent.click(button);
    waitFor(() => expect(setTriggerStopAudio).toBeCalledWith(true));
  });

  it('Doesnt stop audio alert when connection restored and user confirms but alert was playing beore', async () => {
    mockIsOnline = false;
    const setTriggerStopAudio = jest.fn();

    const { rerender } = render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            setAudioAlert: jest.fn(),
            setActiveAlertsExist: jest.fn(),
            setTriggerStopAudio,
          }}
        >
          <SessionContext>
            <NetworkManager />
          </SessionContext>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    mockIsOnline = true;

    rerender(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            setTriggerStopAudio,
          }}
        >
          <SessionContext>
            <NetworkManager />
          </SessionContext>
        </AudioManager.Provider>
      </QueryClientProvider>
    );
    const button = screen.getByRole('button', { name: 'Ok' });
    expect(button).toBeInTheDocument();
    fireEvent.click(button);
    waitFor(() => expect(setTriggerStopAudio).not.toBeCalledWith(true));
  });
});
