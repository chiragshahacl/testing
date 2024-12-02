import useSession from '@/hooks/useSession';

/**
 * @description Checks if the current user is authenticated
 * @returns true if there is an accessToken stored. false otherwise
 */
const useIsUserAuthenticated = (): boolean => {
  const { accessToken } = useSession();
  return !!accessToken;
};

export { useIsUserAuthenticated };
