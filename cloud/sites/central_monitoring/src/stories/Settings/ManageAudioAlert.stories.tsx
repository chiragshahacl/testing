import ManageAudioAlert from '@/components/Settings/ManageAudioAlert';
import { ALERT_AUDIO } from '@/constants';
import { AudioManager } from '@/context/AudioManagerContext';
import { expect, jest } from '@storybook/jest';
import type { Meta, StoryObj } from '@storybook/react';
import { screen, userEvent, waitFor } from '@storybook/testing-library';
import { rest } from 'msw';

const updateAudioSetting = jest.fn();

const meta: Meta<typeof ManageAudioAlert> = {
  component: ManageAudioAlert,
  args: {
    isOpen: true,
  },
  decorators: [
    (Story) => {
      updateAudioSetting.mockReset();

      return (
        <AudioManager.Provider
          value={{
            audioAlarmSetting: ALERT_AUDIO.ON,
            updateAudioSetting,
            startCurrentAudioFile: jest.fn(),
            pauseAudio: jest.fn(),
            stopAlertSound: jest.fn(),
            audioIsActive: true,
            setAudioIsActive: jest.fn(),
            audioDisabledTimer: 120,
            setAudioDisabledTimer: jest.fn(),
            setTriggerStopAudio: jest.fn(),
            autoPlayActivated: false,
            setAutoPlayActivated: jest.fn(),
            activeAlertsExist: false,
            setActiveAlertsExist: jest.fn(),
            timerIsPaused: false,
            setTimerIsPaused: jest.fn(),
            setAudioAlert: jest.fn(),
            currentAlertPriority: null,
          }}
        >
          <Story />
        </AudioManager.Provider>
      );
    },
  ],
  parameters: {
    msw: {
      handlers: [
        rest.post('/web/auth/token', (req, res, ctx) => {
          return res(ctx.status(200));
        }),
      ],
    },
  },
};

export default meta;
type Story = StoryObj<typeof ManageAudioAlert>;

export const InitialState: Story = {
  play: async () => {
    expect(screen.getByTestId('audio_on')).toBeInTheDocument();
    expect(screen.getByTestId('save-button')).toBeDisabled();
  },
};

export const NewAudioSetting: Story = {
  play: async () => {
    expect(screen.getByTestId('save-button')).toBeDisabled();
    await userEvent.click(screen.getByTestId('audio_on'), {
      pointerEventsCheck: 0,
    });
    await expect(screen.getByTestId('save-button')).not.toBeDisabled();
  },
};

export const UnchangedAudioSetting: Story = {
  play: async (context) => {
    await NewAudioSetting.play?.(context);
    await userEvent.click(screen.getByTestId('audio_off'), {
      pointerEventsCheck: 0,
    });
    await expect(screen.getByTestId('save-button')).toBeDisabled();
  },
};

export const UnsavedChanges: Story = {
  play: async (context) => {
    await NewAudioSetting.play?.(context);
    await userEvent.click(screen.getByTestId('dismiss-modal'));
    await expect(context.args.onSetOpen).toHaveBeenCalledWith(false);
    await expect(screen.getByText('Unsaved changes')).toBeInTheDocument();
  },
};

export const DiscardUnsavedChanges: Story = {
  play: async (context) => {
    await UnsavedChanges.play?.(context);
    await userEvent.click(screen.getByTestId('discard-button'));
    await expect(context.args.onSetOpen).toHaveBeenCalledWith(false);
  },
};

export const BackToEdit: Story = {
  play: async (context) => {
    await UnsavedChanges.play?.(context);
    await userEvent.click(screen.getByTestId('back-to-edit-button'));
    await expect(screen.queryByText('Unsaved changes')).not.toBeInTheDocument();
    await expect(screen.getByTestId('audio_off')).toBeInTheDocument();
  },
};

export const SaveNewSetting: Story = {
  play: async (context) => {
    await NewAudioSetting.play?.(context);
    await userEvent.click(screen.getByTestId('save-button'));
    await expect(screen.getByText('Password required')).toBeInTheDocument();
    await expect(
      screen.getByText(
        'All audible alarms at Central Station will be silenced until manually activated. Please enter the password to save alarm settings.'
      )
    ).toBeInTheDocument();
    await expect(screen.getByTestId('submit-button')).toBeDisabled();
  },
};

export const BackToManageAudio: Story = {
  play: async (context) => {
    await SaveNewSetting.play?.(context);
    await userEvent.click(screen.getByTestId('back-to-edit-button'));
    await expect(screen.getByTestId('audio_off')).toBeInTheDocument();
    await expect(screen.getByTestId('save-button')).not.toBeDisabled();
  },
};

export const IncorrectPassword: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.post('/web/auth/token', (req, res, ctx) => {
          return res(ctx.status(401));
        }),
      ],
    },
  },
  play: async (context) => {
    await NewAudioSetting.play?.(context);
    await userEvent.click(screen.getByTestId('save-button'));

    const passwordInput = screen.getByPlaceholderText('Password');

    await userEvent.type(passwordInput, 'password');
    await expect(screen.getByTestId('submit-button')).not.toBeDisabled();
    await userEvent.click(screen.getByTestId('submit-button'));
    await waitFor(() => {
      expect(screen.getByText('Incorrect password. Please try again.')).toBeInTheDocument();
    });
  },
};

export const ServerError: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.post('/web/auth/token', (req, res, ctx) => {
          return res(ctx.status(500));
        }),
      ],
    },
  },
  play: async (context) => {
    await NewAudioSetting.play?.(context);
    await userEvent.click(screen.getByTestId('save-button'));

    const passwordInput = screen.getByPlaceholderText('Password');

    await userEvent.type(passwordInput, 'password');
    await expect(screen.getByTestId('submit-button')).not.toBeDisabled();
    await userEvent.click(screen.getByTestId('submit-button'));
    await waitFor(() => {
      expect(
        screen.getByText('Server error. Please try again in a few minutes.')
      ).toBeInTheDocument();
    });
  },
};

export const DiscardPasswordValidation: Story = {
  play: async (context) => {
    await SaveNewSetting.play?.(context);
    await waitFor(() => {
      userEvent.click(screen.getByTestId('dismiss-modal'));
    });
    await waitFor(() => {
      expect(screen.getByText('Unsaved changes')).toBeInTheDocument();
    });
    await userEvent.click(screen.getByTestId('discard-button'));
    await expect(context.args.onSetOpen).toHaveBeenCalledWith(false);
    await expect(screen.getByTestId('audio_on')).toBeInTheDocument();
  },
};

export const Success: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.post('/web/auth/token', (req, res, ctx) => {
          return res(ctx.status(200));
        }),
      ],
    },
  },
  play: async (context) => {
    const localStorageSpy = jest.spyOn(localStorage, 'setItem');

    await NewAudioSetting.play?.(context);
    await userEvent.click(screen.getByTestId('save-button'));

    const passwordInput = screen.getByPlaceholderText('Password');

    await userEvent.type(passwordInput, 'password');
    await expect(screen.getByTestId('submit-button')).not.toBeDisabled();
    await userEvent.click(screen.getByTestId('submit-button'));
    await waitFor(() => {
      expect(screen.getByText('Alarm settings updated')).toBeInTheDocument();
      expect(
        screen.getByText('Alarm settings have been successfully updated.')
      ).toBeInTheDocument();
      expect(localStorageSpy).toHaveBeenCalledWith('alertAudioSetting', 'audio_off');
      expect(updateAudioSetting).toHaveBeenCalled();
    });
  },
};
