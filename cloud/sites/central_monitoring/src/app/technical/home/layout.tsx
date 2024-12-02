'use client';

import AutoLogoutWrapper from '@/components/layout/AutoLogoutWrapper';
import { USER_TYPE } from '@/constants';
import useSession from '@/hooks/useSession';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

interface RootLayoutProps {
  children: React.ReactNode;
}

const RootLayout = ({ children }: RootLayoutProps) => {
  const router = useRouter();
  const { accessToken, refreshToken, authenticating, userType } = useSession();

  useEffect(() => {
    // Redirects to login if not authenticated
    if (!authenticating && !(accessToken && refreshToken && userType == USER_TYPE.TECH)) {
      router.replace('/technical/login');
    }
  }, [accessToken, authenticating, refreshToken, router, userType]);

  return <AutoLogoutWrapper>{children}</AutoLogoutWrapper>;
};

export default RootLayout;
