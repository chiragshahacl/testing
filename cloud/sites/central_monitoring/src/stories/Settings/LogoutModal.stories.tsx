import LogoutModal from '@/components/modals/LogoutModal';
import { ALERT_AUDIO } from '@/constants';
import { AudioManager } from '@/context/AudioManagerContext';
import { PatientsData } from '@/context/PatientsContext';
import { STORAGE_KEYS } from '@/utils/storage';
import { action } from '@storybook/addon-actions';
import { expect, jest } from '@storybook/jest';
import { Meta, StoryObj } from '@storybook/react';
import { screen, userEvent, waitFor } from '@storybook/testing-library';
import { rest } from 'msw';

const onReplace = jest.fn();
const removeSelfFromBedsDisplayGroup = jest.fn();
const startCurrentAudioFile = jest.fn();
const pauseAudio = jest.fn();
const stopAlertSound = jest.fn();
const setAudioDisabledTimer = jest.fn();
const setAudioIsActive = jest.fn();

const meta: Meta<typeof LogoutModal> = {
  component: LogoutModal,
  args: {
    isOpen: true,
  },
  parameters: {
    msw: {
      handlers: [
        rest.post('/web/auth/token/logout', (req, res, ctx) => {
          return res(ctx.status(204));
        }),
      ],
    },
    nextjs: {
      navigation: {
        replace(href: string) {
          onReplace(href);
          return Promise.resolve(true);
        },
      },
    },
  },
  decorators: [
    (Story) => {
      onReplace.mockReset();
      removeSelfFromBedsDisplayGroup.mockReset();
      pauseAudio.mockReset();
      stopAlertSound.mockReset();
      setAudioDisabledTimer.mockReset();
      setAudioIsActive.mockReset();
      return (
        <PatientsData.Provider
          value={{
            removeSelfFromBedsDisplayGroup,
            selectedBed: {
              id: 'B-001',
              bedNo: 'B-001',
            },
            updateSelectedBed: action('onUpdateSelectedBed'),
            loadingSelectedBed: false,
            getGroupById: jest.fn(),
            getActiveGroup: jest.fn(),
            updateActiveGroup: jest.fn(),
            activeGroupId: '',
            setBedManagementModal: jest.fn(),
            bedManagementModalIsOpen: false,
            resetPatientsContext: jest.fn(),
            bedsDisplayGroups: [],
            updateBedsOnDisplay: jest.fn(),
            bedsDisplayGroupsKeepAlive: jest.fn(),
            groupManagementModalIsOpen: false,
            setGroupManagementModal: jest.fn(),
            monitorsFreshDataKeepAlive: {
              current: {},
            },
            resetMonitorsKeepAlive: jest.fn(),
            updateKeepAlive: jest.fn(),
          }}
        >
          <AudioManager.Provider
            value={{
              startCurrentAudioFile,
              pauseAudio,
              stopAlertSound,
              audioAlarmSetting: ALERT_AUDIO.ON,
              audioIsActive: false,
              setAudioIsActive: jest.fn(),
              audioDisabledTimer: 120,
              setAudioDisabledTimer: jest.fn(),
              setTriggerStopAudio: jest.fn(),
              autoPlayActivated: true,
              setAutoPlayActivated: jest.fn(),
              activeAlertsExist: false,
              setActiveAlertsExist: jest.fn(),
              timerIsPaused: false,
              setTimerIsPaused: jest.fn(),
              setAudioAlert: jest.fn(),
              updateAudioSetting: jest.fn(),
              currentAlertPriority: null,
            }}
          >
            <Story />
          </AudioManager.Provider>
        </PatientsData.Provider>
      );
    },
  ],
};

export default meta;
type Story = StoryObj<typeof LogoutModal>;

export const Default: Story = {
  play: async () => {
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByTestId('submit-button');

    await expect(passwordInput).toBeInTheDocument();
    await expect(submitButton).toBeInTheDocument();
    await expect(submitButton).toBeDisabled();
  },
};

export const Filled: Story = {
  play: async () => {
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByTestId('submit-button');

    await expect(submitButton).toBeDisabled();
    await userEvent.type(passwordInput, 'password');
    await expect(submitButton).not.toBeDisabled();
  },
};

export const SuccessWithAudio: Story = {
  play: async () => {
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();
      expect(screen.getByTestId('submit-button')).toBeInTheDocument();
    });

    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByTestId('submit-button');

    expect(submitButton).toBeDisabled();
    await userEvent.type(passwordInput, 'hi mom');
    expect(submitButton).not.toBeDisabled();
    await userEvent.click(submitButton, { pointerEventsCheck: 0 });

    await waitFor(
      () => {
        expect(onReplace).toHaveBeenCalledWith('/');
        expect(removeSelfFromBedsDisplayGroup).toHaveBeenCalled();
        expect(stopAlertSound).toHaveBeenCalled();
      },
      { timeout: 1500 }
    );
  },
};

export const SuccessWithoutAudio: Story = {
  decorators: [
    (Story, context) => (
      <PatientsData.Provider
        value={{
          removeSelfFromBedsDisplayGroup,
          selectedBed: {
            id: 'B-001',
            bedNo: 'B-001',
          },
          updateSelectedBed: action('onUpdateSelectedBed'),
          loadingSelectedBed: false,
          getGroupById: jest.fn(),
          getActiveGroup: jest.fn(),
          updateActiveGroup: jest.fn(),
          activeGroupId: '',
          setBedManagementModal: jest.fn(),
          bedManagementModalIsOpen: false,
          resetPatientsContext: jest.fn(),
          bedsDisplayGroups: [],
          updateBedsOnDisplay: jest.fn(),
          bedsDisplayGroupsKeepAlive: jest.fn(),
          groupManagementModalIsOpen: false,
          setGroupManagementModal: jest.fn(),
          monitorsFreshDataKeepAlive: {
            current: {},
          },
          resetMonitorsKeepAlive: jest.fn(),
          updateKeepAlive: jest.fn(),
        }}
      >
        <AudioManager.Provider
          value={{
            startCurrentAudioFile,
            pauseAudio,
            stopAlertSound,
            audioAlarmSetting: ALERT_AUDIO.ON,
            audioIsActive: false,
            setAudioIsActive: jest.fn(),
            audioDisabledTimer: 120,
            setAudioDisabledTimer: jest.fn(),
            setTriggerStopAudio: jest.fn(),
            autoPlayActivated: true,
            setAutoPlayActivated: jest.fn(),
            activeAlertsExist: false,
            setActiveAlertsExist: jest.fn(),
            timerIsPaused: false,
            setTimerIsPaused: jest.fn(),
            setAudioAlert: jest.fn(),
            updateAudioSetting: jest.fn(),
            currentAlertPriority: null,
            ...context.args,
          }}
        >
          <Story />
        </AudioManager.Provider>
      </PatientsData.Provider>
    ),
  ],
  play: async () => {
    let accessToken = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByTestId('submit-button');

    await expect(accessToken).not.toBeNull();
    await expect(submitButton).toBeDisabled();
    await userEvent.type(passwordInput, 'hi mom');
    await expect(submitButton).not.toBeDisabled();
    await userEvent.click(submitButton, { pointerEventsCheck: 0 });

    await waitFor(
      () => {
        expect(onReplace).toHaveBeenCalledWith('/');
        expect(removeSelfFromBedsDisplayGroup).toHaveBeenCalled();
      },
      { timeout: 1000 }
    );
    accessToken = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    await expect(accessToken).toBeNull();
  },
};

export const SuccessWithAudioPaused: Story = {
  decorators: [
    (Story) => (
      <PatientsData.Provider
        value={{
          removeSelfFromBedsDisplayGroup,
          selectedBed: {
            id: 'B-001',
            bedNo: 'B-001',
          },
          updateSelectedBed: action('onUpdateSelectedBed'),
          loadingSelectedBed: false,
          getGroupById: jest.fn(),
          getActiveGroup: jest.fn(),
          updateActiveGroup: jest.fn(),
          activeGroupId: '',
          setBedManagementModal: jest.fn(),
          bedManagementModalIsOpen: false,
          resetPatientsContext: jest.fn(),
          bedsDisplayGroups: [],
          updateBedsOnDisplay: jest.fn(),
          bedsDisplayGroupsKeepAlive: jest.fn(),
          groupManagementModalIsOpen: false,
          setGroupManagementModal: jest.fn(),
          monitorsFreshDataKeepAlive: {
            current: {},
          },
          resetMonitorsKeepAlive: jest.fn(),
          updateKeepAlive: jest.fn(),
        }}
      >
        <AudioManager.Provider
          value={{
            setAudioDisabledTimer,
            setAudioIsActive,
            startCurrentAudioFile,
            pauseAudio,
            stopAlertSound,
            audioAlarmSetting: ALERT_AUDIO.ON,
            audioIsActive: false,
            audioDisabledTimer: 120,
            setTriggerStopAudio: jest.fn(),
            autoPlayActivated: true,
            setAutoPlayActivated: jest.fn(),
            activeAlertsExist: false,
            setActiveAlertsExist: jest.fn(),
            timerIsPaused: false,
            setTimerIsPaused: jest.fn(),
            setAudioAlert: jest.fn(),
            updateAudioSetting: jest.fn(),
            currentAlertPriority: null,
          }}
        >
          <Story />
        </AudioManager.Provider>
      </PatientsData.Provider>
    ),
  ],
  play: async () => {
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByTestId('submit-button');

    await userEvent.type(passwordInput, 'hi mom');
    await waitFor(() => {
      expect(submitButton).not.toBeDisabled();
    });

    await userEvent.click(submitButton, { pointerEventsCheck: 0 });

    await waitFor(() => {
      expect(onReplace).toHaveBeenCalledWith('/');
      expect(removeSelfFromBedsDisplayGroup).toHaveBeenCalled();
      expect(setAudioDisabledTimer).toHaveBeenCalledWith(120);
      expect(setAudioIsActive).toHaveBeenCalledWith(true);
    });
  },
};

export const IncorrectPassword: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.post('/web/auth/token/logout', (req, res, ctx) => {
          return res(ctx.status(401));
        }),
      ],
    },
  },
  play: async () => {
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByTestId('submit-button');

    await expect(submitButton).toBeDisabled();
    await userEvent.type(passwordInput, 'hi mom');
    await expect(submitButton).not.toBeDisabled();
    await userEvent.click(submitButton, { pointerEventsCheck: 0 });
    await expect(submitButton).toBeDisabled();
    await waitFor(() => {
      expect(screen.getByText('Incorrect password. Please try again.')).toBeInTheDocument();
    });
  },
};

export const InvalidPassword: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.post('/web/auth/token/logout', (req, res, ctx) => {
          return res(ctx.status(422));
        }),
      ],
    },
  },
  play: async () => {
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByTestId('submit-button');

    await expect(submitButton).toBeDisabled();
    await userEvent.type(passwordInput, 'hi mom');
    await expect(submitButton).not.toBeDisabled();
    await userEvent.click(submitButton, { pointerEventsCheck: 0 });
    await expect(submitButton).toBeDisabled();
    await waitFor(() => {
      expect(screen.getByText('Incorrect password. Please try again.')).toBeInTheDocument();
    });
  },
};

export const AccountLocked: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.post('/web/auth/token/logout', (req, res, ctx) => {
          return res(ctx.json({ detail: 'Account locked.' }), ctx.status(401));
        }),
      ],
    },
  },
  play: async () => {
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByTestId('submit-button');

    await expect(submitButton).toBeDisabled();
    await userEvent.type(passwordInput, 'hi mom');
    await expect(submitButton).not.toBeDisabled();
    await userEvent.click(submitButton, { pointerEventsCheck: 0 });
    await expect(submitButton).toBeDisabled();
    await waitFor(() => {
      expect(
        screen.getByText('Too many attempts. Please try again in 15 minutes.')
      ).toBeInTheDocument();
    });
  },
};

export const TooManyAttempts: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.post('/web/auth/token/logout', (req, res, ctx) => {
          return res(ctx.status(429));
        }),
      ],
    },
  },
  play: async () => {
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByTestId('submit-button');

    await expect(submitButton).toBeDisabled();
    await userEvent.type(passwordInput, 'hi mom');
    await expect(submitButton).not.toBeDisabled();
    await userEvent.click(submitButton, { pointerEventsCheck: 0 });
    await expect(submitButton).toBeDisabled();
    await waitFor(() => {
      expect(
        screen.getByText('Too many attempts. Please try again in 15 minutes.')
      ).toBeInTheDocument();
    });
  },
};

/*
 * Requrement IDs: RQ-00022-B: SR-1.1.4.1
 */
export const ServerError: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.post('/web/auth/token/logout', (req, res, ctx) => {
          return res(ctx.status(500));
        }),
      ],
    },
  },
  play: async () => {
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByTestId('submit-button');

    await expect(submitButton).toBeDisabled();
    await userEvent.type(passwordInput, 'hi mom');
    await expect(submitButton).not.toBeDisabled();
    await userEvent.click(submitButton, { pointerEventsCheck: 0 });
    await expect(submitButton).toBeDisabled();
    await waitFor(() => {
      expect(
        screen.getByText('Server error. Please try again in a few minutes.')
      ).toBeInTheDocument();
    });
  },
};

export const Closing: Story = {
  play: async ({ args: { onClose } }) => {
    const closeIcon = screen.getByTestId('dismiss-modal');

    await userEvent.click(closeIcon);
    await expect(onClose).toHaveBeenCalled();
  },
};
