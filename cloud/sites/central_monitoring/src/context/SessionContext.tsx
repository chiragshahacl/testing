import { USER_TYPE } from '@/constants';
import { STORAGE_KEYS } from '@/utils/storage';
import { createContext, useEffect, useState } from 'react';

interface SessionContextProps {
  children: React.ReactNode;
}

type SessionContextType = {
  authenticating: boolean;
  isLoggedIn: boolean;
  accessToken: string | null;
  refreshToken: string | null;
  userType: string | null;
  setUserType: (value: string | null) => void;
  setAccessToken: (value: string | null) => void;
  setRefreshToken: (value: string | null) => void;
  setIsLoggedIn: (value: boolean) => void;
  clearSession: () => void;
};

export const Session = createContext<SessionContextType | null>(null);

/**
 * @description Manages tokens of the current user session and stores information about
 * authentication status.
 * @returns Values provided are session information and methods for updating it. Includes:
 * authenticating - Boolean - True if process of restoring previous user session is in progress
 * isLoggedIn - Boolean - True if user is currently logged in to the system
 * accessToken - String | null - Access token used for communication with realtime and web gateways
 * refreshToken - String | null - Refresh token to re-authenticate a user without going through the
 *      login process again
 * setAccessToken - Method for updating the accessToken
 * setRefreshToken - Method for updating the refreshToken
 * setIsLoggedIn - Method for updating isLoggedIn
 * clearSession - Method for clearing storage associated with user's login status
 */
const SessionContext = ({ children }: SessionContextProps) => {
  const [authenticating, setAuthenticating] = useState<boolean>(true);
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [userType, setUserType] = useState<string | null>(null);

  const clearSession = () => {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER_TYPE);
    setUserType(null);
    setAccessToken(null);
    setRefreshToken(null);
    setIsLoggedIn(false);
  };

  useEffect(() => {
    const handleSecureStorageChange = (event: StorageEvent) => {
      if (event.key === STORAGE_KEYS.ACCESS_TOKEN || event.key === STORAGE_KEYS.REFRESH_TOKEN) {
        setTimeout(() => {
          const updatedAccessToken = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN) as string;
          const updatedRefreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN) as string;
          const updatedUserType = localStorage.getItem(STORAGE_KEYS.USER_TYPE) as string;
          setUserType(updatedUserType || USER_TYPE.NON_TECH);
          setAccessToken(updatedAccessToken);
          setRefreshToken(updatedRefreshToken);
        }, 1000);
      }
    };

    window.addEventListener('storage', handleSecureStorageChange);
    return () => {
      window.removeEventListener('storage', handleSecureStorageChange);
    };
  }, []);

  useEffect(() => {
    const storedAccessToken = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN) as string;
    const storedRefreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN) as string;
    const storedUserType = localStorage.getItem(STORAGE_KEYS.USER_TYPE) as string;
    if (storedAccessToken && storedRefreshToken) {
      setUserType(storedUserType);
      setAccessToken(storedAccessToken);
      setRefreshToken(storedRefreshToken);
      setIsLoggedIn(true);
    }
    setAuthenticating(false);
  }, []);

  return (
    <Session.Provider
      value={{
        authenticating,
        isLoggedIn,
        accessToken,
        refreshToken,
        userType,
        setUserType,
        setAccessToken,
        setRefreshToken,
        setIsLoggedIn,
        clearSession,
      }}
    >
      {children}
    </Session.Provider>
  );
};

export default SessionContext;
