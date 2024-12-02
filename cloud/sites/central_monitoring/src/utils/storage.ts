import { BedsDisplayGroup } from '@/types/patientMonitor';

export enum STORAGE_KEYS {
  USER_TYPE = 'userType',
  ACCESS_TOKEN = 'accessToken',
  REFRESH_TOKEN = 'refreshToken',
  DISPLAYED_BEDS = 'displayedBeds',
  SCREEN_HANDLING_SOUND = 'screenHandlingSound',
  ALERT_AUDIO_SETTING = 'alertAudioSetting',
  ALERT_AUDIO_PAUSED = 'alertAudioPause',
  SESSION_EXPIRY_TIME = 'sessionExpiry',
}

/**
 * Retrieves the beds that are currently being displayed by any screen with the same
 * user navigation session in users computer
 */
export const getStoredDisplayedBeds = () => {
  const bedsOnDisplayString = localStorage.getItem(STORAGE_KEYS.DISPLAYED_BEDS);
  if (bedsOnDisplayString) {
    return JSON.parse(bedsOnDisplayString) as BedsDisplayGroup[];
  }
  return [];
};

/**
 * Saves the beds that are currently being displayed in the current screen to be
 * accesed by all screens of the same user session in users computer
 */
export const saveStoredDisplayedBeds = (newBedsOnDisplay: BedsDisplayGroup[]) => {
  localStorage.setItem(STORAGE_KEYS.DISPLAYED_BEDS, JSON.stringify(newBedsOnDisplay));
  window.dispatchEvent(new Event('bedsDisplayGroupsUpdated'));
};
