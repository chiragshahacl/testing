import { useHealthcheck } from '@/api/useHealthcheck';
import { ALERT_AUDIO, AUDIO_DISABLED_TIMER } from '@/constants';
import useNetwork from '@/hooks/useNetwork';
import { Alert } from '@/types/alerts';
import { AudioHandlingScreen } from '@/types/screens';
import { getAlertPriorityValue, getHighestPriorityFromAlerts } from '@/utils/alertUtils';
import { ALERT_PRIORITY } from '@/utils/metricCodes';
import { STORAGE_KEYS } from '@/utils/storage';
import moment from 'moment';
import {
  Dispatch,
  ReactNode,
  SetStateAction,
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import { v4 as uuidv4 } from 'uuid';

interface AudioManagerContextProps {
  children: ReactNode;
}

type AudioManagerContextType = {
  audioAlarmSetting: ALERT_AUDIO;
  audioIsActive: boolean;
  setAudioIsActive: (value: boolean) => void;
  audioDisabledTimer: number;
  setAudioDisabledTimer: Dispatch<SetStateAction<number>>;
  startCurrentAudioFile: () => void;
  pauseAudio: () => void;
  stopAlertSound: () => void;
  setTriggerStopAudio: (value: boolean) => void;
  autoPlayActivated: boolean;
  setAutoPlayActivated: (value: boolean) => void;
  activeAlertsExist: boolean;
  setActiveAlertsExist: (value: boolean) => void;
  timerIsPaused: boolean;
  setTimerIsPaused: (value: boolean) => void;
  setAudioAlert: (alerts: Alert[], override?: boolean) => void;
  currentAlertPriority: ALERT_PRIORITY | null;
  updateAudioSetting: () => void;
};

const AudioIntervals: Record<ALERT_PRIORITY, number> = {
  [ALERT_PRIORITY.LOW]: 16000,
  [ALERT_PRIORITY.MEDIUM]: 7000,
  [ALERT_PRIORITY.HIGH]: 4500,
  [ALERT_PRIORITY.INTERNAL]: 0,
};

export const AudioManager = createContext<AudioManagerContextType | null>(null);
const SCREEN_ID = uuidv4();
const AUDIO_HANDLER_TIMEOUT = 10000;

/**
 * @description Manages all aspects regarding to audio throughout CMS. This includes
 * playing alert audio continuously, handling which alarm sound to play,
 * pausing or silencing audio, handling pause timer to automatically restart.
 * If audio is silenced it will not produce more sound until manually activated.
 * If audio is paused it will trigger sound again if applicable after 2 minutes
 * or until manually upaused
 * @returns Values provided are: status of CMS audio and methods for handling alert audio playing. Includes:
 * audioAlarmSetting - ALERT_AUDIO. Indicates if global CMS audio is silenced
 * updateAudioSetting - Method for updating the audioAlarmSetting based on what is
 *      saved in local storage on ALERT_AUDIO_SETTING (used for multi-windows flows)
 * audioIsActive - Boolean. Indicates if global CMS audio is currently active
 * setAudioIsActive - Method for updating value of audioIsActive
 * timerIsPaused - Boolean. Indicates if global CMS audio has been paused
 * setTimerIsPaused - Method for updating value of timerIsPaused
 * audioDisabledTimer - Number. Indicates amount of seconds remaining before audio is
 *      unpaused automatically
 * setAudioDisabledTimer - Method for updating value of audioDisabledTimer
 * startCurrenetAudioFile - Method for starting audio play
 * pauseAudio - Method for directly pausing all audio files
 * stopAlertSound - Method for resetting audio state
 * setTriggerStopAudio - Method for triggering audio pausing from threads other than
 *      CMS thread
 * autoPlayActivated - Boolean. Indicates if audio is available to be played regarding
 *      browser restrictions. Supported browser does not allow audio play if user
 *      has not interacted with the application yet.
 * setAutoPlayActivated - Method for updating value of autoPlayActivated
 * activeAlertsExist - Boolean. Indicates if there is currently an alert that should
 *      be playing
 * setActiveAlertsExist - Method for setting activeAlertsExist
 * setAudioAlert - Method for setting the appropriate audio file to be played from a particular
 *      set of received alerts
 * currentAlertPriority - ALERT_PRIORITY | null. Priority of the currently running alert
 */
const AudioManagerContext = ({ children }: AudioManagerContextProps): JSX.Element => {
  const [audioIsActive, setAudioIsActive] = useState(true);
  const [activeAlertsExist, setActiveAlertsExist] = useState(false);
  const [audioAlarmSetting, setAudioAlarmSetting] = useState<ALERT_AUDIO>(ALERT_AUDIO.ON);
  const [audioDisabledTimer, setAudioDisabledTimer] = useState<number>(AUDIO_DISABLED_TIMER);
  const [currentAlertPriority, setCurrentAlertPriority] = useState<ALERT_PRIORITY | null>(null);
  const [triggerStopAudio, setTriggerStopAudio] = useState<boolean>(false);
  const [autoPlayActivated, setAutoPlayActivated] = useState<boolean>(false);
  const [timerIsPaused, setTimerIsPaused] = useState<boolean>(false);
  const audioPlayingInterval = useRef<NodeJS.Timer | null>(null);
  const keepAliveInterval = useRef<NodeJS.Timer | null>(null);
  const networkIsOnline = useNetwork();
  const serverIsOnline = useHealthcheck();

  const audioElements: Record<ALERT_PRIORITY, HTMLAudioElement | null> = useMemo(() => {
    if (typeof window !== 'undefined') {
      const lowAudioElement = new Audio('lowAlertAudio.wav');
      const medAudioElement = new Audio('medAlertAudio.wav');
      const highAudioElement = new Audio('highAlertAudio.wav');

      return {
        [ALERT_PRIORITY.LOW]: lowAudioElement,
        [ALERT_PRIORITY.MEDIUM]: medAudioElement,
        [ALERT_PRIORITY.HIGH]: highAudioElement,
        [ALERT_PRIORITY.INTERNAL]: null,
      };
    }
    return {
      [ALERT_PRIORITY.LOW]: null,
      [ALERT_PRIORITY.MEDIUM]: null,
      [ALERT_PRIORITY.HIGH]: null,
      [ALERT_PRIORITY.INTERNAL]: null,
    };
  }, []);

  const pauseAudio = useCallback(() => {
    if (audioPlayingInterval.current) {
      clearInterval(audioPlayingInterval.current);
      audioPlayingInterval.current = null;
    }
    Object.values(audioElements).forEach((audioElement) => {
      if (audioElement) {
        audioElement.pause();
        audioElement.currentTime = 0;
      }
    });
  }, [audioElements]);

  const startCurrentAudioFile = useCallback(() => {
    if (activeAlertsExist) {
      if (
        audioAlarmSetting === ALERT_AUDIO.ON &&
        audioIsActive &&
        autoPlayActivated &&
        currentAlertPriority
      ) {
        if (!audioPlayingInterval.current) {
          const playInterval = setInterval(() => {
            startCurrentAudioFile();
          }, AudioIntervals[currentAlertPriority]);
          audioPlayingInterval.current = playInterval;
        }
        const updatedScreenHandlingSound: AudioHandlingScreen = JSON.parse(
          localStorage.getItem(STORAGE_KEYS.SCREEN_HANDLING_SOUND) || '{}'
        ) as AudioHandlingScreen;
        if (
          !updatedScreenHandlingSound.screen ||
          updatedScreenHandlingSound.screen === SCREEN_ID ||
          !updatedScreenHandlingSound.timestamp ||
          updatedScreenHandlingSound.timestamp + AUDIO_HANDLER_TIMEOUT < moment.now() ||
          !updatedScreenHandlingSound.priority ||
          (updatedScreenHandlingSound.priority &&
            getAlertPriorityValue(currentAlertPriority) >
              getAlertPriorityValue(updatedScreenHandlingSound.priority))
        ) {
          setScreenAsAudioHandler(currentAlertPriority);
          Object.entries(audioElements).forEach(([priority, audioElement]) => {
            if (!audioElement) return;
            if (currentAlertPriority !== priority) {
              audioElement.pause();
              audioElement.currentTime = 0;
            } else {
              audioElement.play().catch(() => {
                // Play may fail because user has yet to interact with screen. This is expected
              });
            }
          });
        } else {
          pauseAudio();
        }
      }
    } else {
      if (audioPlayingInterval.current) {
        clearInterval(audioPlayingInterval.current);
        audioPlayingInterval.current = null;
      }
    }
  }, [
    activeAlertsExist,
    audioAlarmSetting,
    audioElements,
    audioIsActive,
    autoPlayActivated,
    currentAlertPriority,
    pauseAudio,
  ]);

  const setScreenAsAudioHandler = (priority: ALERT_PRIORITY) => {
    const screenInfo: AudioHandlingScreen = {
      screen: SCREEN_ID,
      timestamp: moment.now(),
      priority,
    };
    localStorage.setItem(STORAGE_KEYS.SCREEN_HANDLING_SOUND, JSON.stringify(screenInfo));

    if (!keepAliveInterval.current) {
      const intervalCallback = setInterval(() => {
        const savedScreenInfo: AudioHandlingScreen = JSON.parse(
          localStorage.getItem(STORAGE_KEYS.SCREEN_HANDLING_SOUND) || '{}'
        ) as AudioHandlingScreen;
        if (savedScreenInfo.screen === SCREEN_ID) {
          const screenInfo: AudioHandlingScreen = {
            ...savedScreenInfo,
            timestamp: moment.now(),
          };
          localStorage.setItem(STORAGE_KEYS.SCREEN_HANDLING_SOUND, JSON.stringify(screenInfo));
        } else {
          if (keepAliveInterval.current) {
            clearInterval(keepAliveInterval.current);
            keepAliveInterval.current = null;
          }
        }
      }, AUDIO_HANDLER_TIMEOUT / 2);

      keepAliveInterval.current = intervalCallback;
    }
  };

  const clearAudioHandler = () => {
    localStorage.setItem(STORAGE_KEYS.SCREEN_HANDLING_SOUND, JSON.stringify({}));
  };

  /**
   *  Sets the audio alert to the highest priority alert
   * @param alerts: array of alerts
   * @param override: if true, will play the audio alert regardless of network/server status
   */
  const setAudioAlert = (alerts: Alert[], override = false) => {
    const isOffline = !serverIsOnline || !networkIsOnline;

    if (isOffline && !override) return;

    const highestAlertPriority = getHighestPriorityFromAlerts(alerts);
    if (highestAlertPriority !== currentAlertPriority) {
      pauseAudio();
      setCurrentAlertPriority(highestAlertPriority);
    }
  };

  const updateAudioSetting = () => {
    const updatedAlertAudioSetting =
      localStorage.getItem(STORAGE_KEYS.ALERT_AUDIO_SETTING) || ALERT_AUDIO.ON;
    if (updatedAlertAudioSetting === ALERT_AUDIO.ON) {
      setTimerIsPaused(false);
      if (!audioIsActive) {
        pauseAudio();
      } else if (activeAlertsExist) startCurrentAudioFile();
    } else {
      setTimerIsPaused(true);
      pauseAudio();
    }
    setAudioAlarmSetting(
      updatedAlertAudioSetting === ALERT_AUDIO.ON ? ALERT_AUDIO.ON : ALERT_AUDIO.OFF
    );
  };

  const stopAlertSound = () => {
    clearAudioHandler();
    pauseAudio();
    setActiveAlertsExist(false);
  };

  useEffect(() => {
    // Stops sound for alerts when triggered
    if (triggerStopAudio) {
      setTriggerStopAudio(false);
      setActiveAlertsExist(false);
      pauseAudio();
    }
  }, [pauseAudio, triggerStopAudio]);

  useEffect(() => {
    // Starts or stops audio depending if audio should be active and if an audio alert exists
    if (!audioIsActive) {
      pauseAudio();
    } else {
      setAudioDisabledTimer(AUDIO_DISABLED_TIMER);
      if (activeAlertsExist) startCurrentAudioFile();
    }
  }, [audioIsActive, activeAlertsExist, pauseAudio, startCurrentAudioFile]);

  useEffect(() => {
    // Starts audio file after setting a new alert priority
    // This is an effect since we need to wait until priority is set on state
    pauseAudio();
    if (currentAlertPriority && autoPlayActivated) {
      startCurrentAudioFile();
    }
  }, [currentAlertPriority, autoPlayActivated, pauseAudio, startCurrentAudioFile]);

  useEffect(() => {
    // Adds listeners for storage events to coordinate audio handling with other CMS screens
    const handleStorageUpdate = (event: StorageEvent) => {
      if (event.key === STORAGE_KEYS.ALERT_AUDIO_PAUSED) {
        const audioPaused = localStorage.getItem(STORAGE_KEYS.ALERT_AUDIO_PAUSED);
        setAudioIsActive(audioPaused === 'true');
      } else if (event.key === STORAGE_KEYS.SCREEN_HANDLING_SOUND) {
        const updatedScreenHandlingSound: AudioHandlingScreen = JSON.parse(
          localStorage.getItem(STORAGE_KEYS.SCREEN_HANDLING_SOUND) || '{}'
        ) as AudioHandlingScreen;
        if (
          updatedScreenHandlingSound &&
          updatedScreenHandlingSound.screen &&
          updatedScreenHandlingSound.screen !== SCREEN_ID
        ) {
          if (keepAliveInterval.current) {
            clearInterval(keepAliveInterval.current);
            keepAliveInterval.current = null;
          }
          pauseAudio();
        } else {
          startCurrentAudioFile();
        }
      } else if (event.key === STORAGE_KEYS.ALERT_AUDIO_SETTING) updateAudioSetting();
    };

    window.addEventListener('storage', handleStorageUpdate);
    window.addEventListener('beforeunload', stopAlertSound);

    return () => {
      window.removeEventListener('storage', handleStorageUpdate);
      window.removeEventListener('beforeunload', stopAlertSound);
    };
  }, [activeAlertsExist, audioElements, pauseAudio, startCurrentAudioFile, stopAlertSound]);

  useEffect(() => {
    return () => {
      pauseAudio();
      Object.values(audioElements).forEach((audioElement) => {
        if (!audioElement) return;

        audioElement.loop = false;
        audioElement.srcObject = null;
        audioElement.remove();
      });
      if (keepAliveInterval.current) {
        clearInterval(keepAliveInterval.current);
        keepAliveInterval.current = null;
      }
    };
  }, [audioElements, pauseAudio]);

  return (
    <AudioManager.Provider
      value={{
        audioAlarmSetting,
        audioIsActive,
        setAudioIsActive,
        audioDisabledTimer,
        setAudioDisabledTimer,
        startCurrentAudioFile,
        pauseAudio,
        stopAlertSound,
        setTriggerStopAudio,
        autoPlayActivated,
        setAutoPlayActivated,
        activeAlertsExist,
        setActiveAlertsExist,
        timerIsPaused,
        setTimerIsPaused,
        setAudioAlert,
        currentAlertPriority,
        updateAudioSetting,
      }}
    >
      {children}
    </AudioManager.Provider>
  );
};

export default AudioManagerContext;
