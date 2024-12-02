'use client';
import useSession from '@/hooks/useSession';
import { useCallback, useEffect, useRef, type PropsWithChildren } from 'react';
import moment from 'moment';
import { STORAGE_KEYS } from '@/utils/storage';
import { ACTIVE_SESSION_KEY } from '@/constants';

const windowEvents: WindowActivityEvent[] = ['click', 'mousemove', 'keypress', 'scroll'];

type WindowActivityEvent = keyof WindowEventMap;

interface AutoLogoutProviderProps extends PropsWithChildren {
  timeoutMs?: number;
}

const AutoLogoutWrapper = ({ timeoutMs = 900000, children }: AutoLogoutProviderProps) => {
  const onTimerElapsed = () => isUserInactive();

  const intervalId = useRef<number>();

  const { isLoggedIn, clearSession } = useSession();

  const isUserInactive = useCallback(() => {
    const now = moment();
    const expiry = localStorage.getItem(STORAGE_KEYS.SESSION_EXPIRY_TIME);

    if (isLoggedIn) {
      if (moment(expiry).isBefore(now)) {
        clearSession();
        sessionStorage.removeItem(ACTIVE_SESSION_KEY);
        return true;
      }
    }

    return false;
  }, [isLoggedIn, clearSession]);

  const handleUserActivity = useCallback(() => {
    clearInterval(intervalId.current);
    intervalId.current = window.setInterval(() => {
      onTimerElapsed();
    }, timeoutMs);
    localStorage.setItem(
      STORAGE_KEYS.SESSION_EXPIRY_TIME,
      moment().add(timeoutMs, 'milliseconds').format()
    );
  }, []);

  useEffect(() => {
    if (!isLoggedIn) return;

    handleUserActivity();

    windowEvents.forEach((eventName) => {
      window.addEventListener(eventName, handleUserActivity, false);
    });

    return () => {
      windowEvents.forEach((eventName) => {
        window.removeEventListener(eventName, handleUserActivity, false);
      });
      window.clearInterval(intervalId.current);
    };
  }, [isLoggedIn]);

  return <>{children}</>;
};

export default AutoLogoutWrapper;
