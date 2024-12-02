import useSession from '@/hooks/useSession';
import { ServerErrorResponse } from '@/types/response';
import { logoutClient } from '@/utils/httpClient';
import { STORAGE_KEYS } from '@/utils/storage';
import { useMutation } from '@tanstack/react-query';
import { useCallback, useEffect } from 'react';

export type LogoutRequest = {
  password: string;
};
type LogoutResponse = null;

const logout = async (data: LogoutRequest): Promise<LogoutResponse> => {
  return logoutClient.post('/web/auth/token/logout', data);
};

export const useLogout = () => {
  const { setRefreshToken, setAccessToken, setIsLoggedIn, clearSession } = useSession();

  const handleInterceptorLogoutEvent = useCallback(() => {
    setAccessToken(null);
    setRefreshToken(null);
    setIsLoggedIn(false);
  }, [setAccessToken, setIsLoggedIn, setRefreshToken]);

  useEffect(() => {
    // Listenes for logout events to remove session information
    window.addEventListener('logout', handleInterceptorLogoutEvent);

    return () => {
      window.removeEventListener('logout', handleInterceptorLogoutEvent);
    };
  }, [handleInterceptorLogoutEvent]);

  const { mutateAsync, ...rest } = useMutation<LogoutResponse, ServerErrorResponse, LogoutRequest>({
    mutationFn: logout,
    mutationKey: ['logout'],
    onSuccess: () => {
      clearSession();
    },
  });
  return { logout: mutateAsync, ...rest };
};
