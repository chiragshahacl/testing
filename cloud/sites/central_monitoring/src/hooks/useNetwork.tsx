'use client';
import useDebounce from '@/hooks/useDebounce';
import { useEffect, useState } from 'react';

/**
 * @description A hook to check if the user is online or not.
 * @returns A boolean.
 */
const useNetwork = (): boolean => {
  const [isOnline, setNetwork] = useState<boolean>(true);

  const updateNetwork = useDebounce(() => {
    setNetwork(window.navigator.onLine);
  }, 2000);

  useEffect(() => {
    // Handles listener for network going offline/online
    window.addEventListener('offline', updateNetwork);

    window.addEventListener('online', updateNetwork);

    return () => {
      window.removeEventListener('offline', updateNetwork);

      window.removeEventListener('online', updateNetwork);
    };
  });

  return isOnline;
};

export default useNetwork;
