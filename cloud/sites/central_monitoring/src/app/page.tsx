'use client';

import { refreshTokenRequest } from '@/api/authApi';
import useSession from '@/hooks/useSession';
import { isTokenValid } from '@/utils/jwtToken';
import { useRouter } from 'next/navigation';
import { useCallback, useEffect } from 'react';
import Loading from './loading';
import useTypedSearchParams from '@/hooks/useTypedSearchParams';
import { USER_TYPE } from '@/constants';

/**
 * Detects if the user currently has a valid token. Redirects to the home view if so, or
 * redirects to login screen if not authenticated
 */
const Authentication = () => {
  const router = useRouter();
  const searchParams = useTypedSearchParams();
  const { authenticating, isLoggedIn, refreshToken, userType } = useSession();

  const handleAutoLogin = useCallback(async () => {
    if (refreshToken && isTokenValid(refreshToken)) {
      await refreshTokenRequest({ refresh: refreshToken });
      const defaultGroup = searchParams.groupIndex;
      if (defaultGroup) {
        router.replace(`/home?groupIndex=${defaultGroup}`);
      } else {
        if (userType === USER_TYPE.TECH) router.replace('/technical/home');
        else router.replace('/home');
      }
    } else {
      router.replace('/login');
    }
  }, [refreshToken, router, searchParams.groupIndex]);

  useEffect(() => {
    // Fire auto login if user finished authenticating or in case
    // there are multiple windows running this site
    if (!authenticating && isLoggedIn) void handleAutoLogin();
    if (!authenticating && !isLoggedIn) router.replace('/login');
  }, [authenticating, handleAutoLogin, isLoggedIn, router]);

  return <Loading />;
};

export default Authentication;
