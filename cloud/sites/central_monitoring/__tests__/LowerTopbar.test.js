import { ThemeProvider } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import React, { useState } from 'react';

import theme from '@/theme/theme';

import { useGroups } from '@/api/useGroups';
import LowerTopbar from '@/components/layout/LowerTopbar';
import { ALERT_AUDIO } from '@/constants';
import AudioManagerContext, { AudioManager } from '@/context/AudioManagerContext';
import PatientsContext, { PatientsData } from '@/context/PatientsContext';
import SessionContext from '@/context/SessionContext';
import { MockGroups } from '@/utils/groupsMockData';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 0,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
    },
  },
});

const mockUseGroups = useGroups;
jest.mock('@/api/useGroups');

const AudioManagerProviderMock = ({ children }) => {
  const [audioAlarmSetting, setAudioAlarmSetting] = useState(ALERT_AUDIO.ON);
  const [audioIsActive, setAudioIsActive] = useState(true);
  const [audioDisabledTimer, setAudioDisabledTimer] = useState(120);

  return (
    <AudioManager.Provider
      value={{
        audioAlarmSetting,
        setAudioAlarmSetting,
        audioIsActive,
        setAudioIsActive,
        audioDisabledTimer,
        setAudioDisabledTimer,
      }}
    >
      {children}
    </AudioManager.Provider>
  );
};

describe('LowerTopbar', () => {
  beforeAll(() => {
    jest.useFakeTimers();
  });
  it('renders all components', async () => {
    mockUseGroups.mockImplementation(() => ({
      data: MockGroups,
      isPlaceholderData: false,
      isSuccess: true,
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <SessionContext>
            <AudioManagerProviderMock>
              <PatientsContext>
                <LowerTopbar
                  setShowSettings={jest.fn()}
                  showSettings={false}
                  customUpdateGroup={jest.fn()}
                />
              </PatientsContext>
            </AudioManagerProviderMock>
          </SessionContext>
        </ThemeProvider>
      </QueryClientProvider>
    );

    expect(screen.getByAltText('anne-stream-logo')).toBeInTheDocument();
    expect(screen.getByText('Central Audio on')).toBeInTheDocument();
    expect(screen.getByText('Bed Management')).toBeInTheDocument();
    expect(screen.getByText('Group Management')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.1.6.6 RQ-00022-B: SR-1.1.6.8, SR-1.1.6.1, SR-1.1.6.13, SR-1.1.6.15, SR-1.1.6.16, SR-1.1.6.17, SR-1.1.6.19, SR-1.1.6.21, SR-1.1.6.22
   * RQ-00022-B: SR-1.1.6.9, SR-1.1.6.1, SR-1.1.6.13, SR-1.1.6.15, SR-1.1.6.16, SR-1.1.6.17, SR-1.1.6.18, SR-1.1.6.21 RQ-00022-B: SR-1.8.1.9
   */
  it('toggles audio', async () => {
    mockUseGroups.mockImplementation(() => ({
      data: MockGroups,
      isPlaceholderData: false,
      isSuccess: true,
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <SessionContext>
            <AudioManagerProviderMock>
              <PatientsContext>
                <LowerTopbar
                  setShowSettings={jest.fn()}
                  showSettings={false}
                  customUpdateGroup={jest.fn()}
                />
              </PatientsContext>
            </AudioManagerProviderMock>
          </SessionContext>
        </ThemeProvider>
      </QueryClientProvider>
    );

    expect(screen.getByText('Pause')).toBeInTheDocument();
    fireEvent.click(screen.getByText('Pause'));
    await waitFor(() => {
      expect(screen.getByText('Central Audio Paused 02:00')).toBeInTheDocument();
    });
    expect(screen.getByText('Cancel')).toBeInTheDocument();
    fireEvent.click(screen.getByText('Cancel'));
    await waitFor(() => {
      expect(screen.getByText('Pause')).toBeInTheDocument();
    });
  });

  it('shows audio off', async () => {
    mockUseGroups.mockImplementation(() => ({
      data: MockGroups,
      isPlaceholderData: false,
      isSuccess: true,
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <SessionContext>
            <AudioManager.Provider
              value={{
                audioAlarmSetting: ALERT_AUDIO.OFF,
                setAudioAlarmSetting: jest.fn(),
                audioIsActive: true,
                setAudioIsActive: jest.fn(),
                audioDisabledTimer: 120,
                setAudioDisabledTimer: jest.fn(),
              }}
            >
              <PatientsContext>
                <LowerTopbar
                  setShowSettings={jest.fn()}
                  showSettings={false}
                  customUpdateGroup={jest.fn()}
                />
              </PatientsContext>
            </AudioManager.Provider>
          </SessionContext>
        </ThemeProvider>
      </QueryClientProvider>
    );

    expect(screen.getByText('Central Audio Off')).toBeInTheDocument();
  });

  it('counts down when audio paused', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <SessionContext>
            <AudioManagerProviderMock>
              <PatientsData.Provider
                value={{
                  activeGroupId: '',
                  updateActiveGroup: jest.fn(),
                }}
              >
                <LowerTopbar
                  setShowSettings={jest.fn()}
                  showSettings={false}
                  customUpdateGroup={jest.fn()}
                />
              </PatientsData.Provider>
            </AudioManagerProviderMock>
          </SessionContext>
        </ThemeProvider>
      </QueryClientProvider>
    );

    fireEvent.click(screen.getByText('Pause'));
    expect(screen.getByText('Central Audio Paused 02:00')).toBeInTheDocument();
    jest.advanceTimersByTime(1000);
    await waitFor(() => {
      expect(screen.getByText('Central Audio Paused 01:59')).toBeInTheDocument();
    });
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.1.6.5
   */
  it('turns on audio after 2 minutes', async () => {
    mockUseGroups.mockImplementation(() => ({
      data: MockGroups,
      isPlaceholderData: false,
      isSuccess: true,
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <SessionContext>
            <AudioManagerProviderMock>
              <PatientsContext>
                <LowerTopbar
                  setShowSettings={jest.fn()}
                  showSettings={false}
                  customUpdateGroup={jest.fn()}
                />
              </PatientsContext>
            </AudioManagerProviderMock>
          </SessionContext>
        </ThemeProvider>
      </QueryClientProvider>
    );

    fireEvent.click(screen.getByText('Pause'));
    expect(screen.getByText('Central Audio Paused 02:00')).toBeInTheDocument();
    jest.advanceTimersByTime(1000 * 121);
    await waitFor(() => {
      expect(screen.getByText('Pause')).toBeInTheDocument();
    });
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.1.6.21
   */
  it('toggles settings', async () => {
    const setShowSettingsMock = jest.fn();
    mockUseGroups.mockImplementation(() => ({
      data: MockGroups,
      isPlaceholderData: false,
      isSuccess: true,
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <SessionContext>
            <AudioManagerContext>
              <PatientsContext>
                <LowerTopbar
                  setShowSettings={setShowSettingsMock}
                  showSettings={false}
                  customUpdateGroup={jest.fn()}
                />
              </PatientsContext>
            </AudioManagerContext>
          </SessionContext>
        </ThemeProvider>
      </QueryClientProvider>
    );

    expect(screen.getByText('Settings')).toBeInTheDocument();
    fireEvent.click(screen.getByText('Settings'));
    expect(setShowSettingsMock).toHaveBeenCalledWith(true);
  });

  it('handles bed management', async () => {
    const setBedManagementModalMock = jest.fn();

    render(
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <SessionContext>
            <AudioManagerContext>
              <PatientsData.Provider
                value={{
                  setBedManagementModal: setBedManagementModalMock,
                }}
              >
                <LowerTopbar
                  setShowSettings={jest.fn()}
                  showSettings={false}
                  customUpdateGroup={jest.fn()}
                />
              </PatientsData.Provider>
            </AudioManagerContext>
          </SessionContext>
        </ThemeProvider>
      </QueryClientProvider>
    );

    expect(screen.getByText('Bed Management')).toBeInTheDocument();
    fireEvent.click(screen.getByText('Bed Management'));
    expect(setBedManagementModalMock).toHaveBeenCalledWith(true);
  });

  it('handles group management', async () => {
    const setGroupManagementModalMock = jest.fn();

    render(
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <SessionContext>
            <AudioManagerContext>
              <PatientsData.Provider
                value={{
                  setGroupManagementModal: setGroupManagementModalMock,
                }}
              >
                <LowerTopbar
                  setShowSettings={jest.fn()}
                  showSettings={false}
                  customUpdateGroup={jest.fn()}
                />
              </PatientsData.Provider>
            </AudioManagerContext>
          </SessionContext>
        </ThemeProvider>
      </QueryClientProvider>
    );

    expect(screen.getByText('Group Management')).toBeInTheDocument();
    fireEvent.click(screen.getByText('Group Management'));
    expect(setGroupManagementModalMock).toHaveBeenCalledWith(true);
  });

  it('sets active group', async () => {
    const customUpdateGroupMock = jest.fn();

    mockUseGroups.mockImplementation(() => ({
      data: MockGroups,
      isPlaceholderData: false,
      isSuccess: true,
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <SessionContext>
            <AudioManagerContext>
              <PatientsContext>
                <LowerTopbar customUpdateGroup={customUpdateGroupMock} />
              </PatientsContext>
            </AudioManagerContext>
          </SessionContext>
        </ThemeProvider>
      </QueryClientProvider>
    );

    expect(screen.getByText('Group 1')).toBeInTheDocument();
    expect(screen.getByText('Group 2')).toBeInTheDocument();
    expect(screen.getByText('Group 3')).toBeInTheDocument();
    expect(screen.getByText('Group 4')).toBeInTheDocument();
    expect(screen.getByText('Group 5')).toBeInTheDocument();
    fireEvent.click(screen.getByText('Group 3'));
    expect(customUpdateGroupMock).toHaveBeenCalledWith('group_3');
  });

  it('sets active group through context', async () => {
    const updateActiveGroupMock = jest.fn();

    mockUseGroups.mockImplementation(() => ({
      data: MockGroups,
      isPlaceholderData: false,
      isSuccess: true,
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <SessionContext>
            <AudioManagerContext>
              <PatientsData.Provider
                value={{
                  updateActiveGroup: updateActiveGroupMock,
                }}
              >
                <LowerTopbar />
              </PatientsData.Provider>
            </AudioManagerContext>
          </SessionContext>
        </ThemeProvider>
      </QueryClientProvider>
    );

    expect(screen.getByText('Group 1')).toBeInTheDocument();
    expect(screen.getByText('Group 2')).toBeInTheDocument();
    expect(screen.getByText('Group 3')).toBeInTheDocument();
    expect(screen.getByText('Group 4')).toBeInTheDocument();
    expect(screen.getByText('Group 5')).toBeInTheDocument();
    fireEvent.click(screen.getByText('Group 3'));
    expect(updateActiveGroupMock).toHaveBeenCalledWith('group_3');
  });
});
