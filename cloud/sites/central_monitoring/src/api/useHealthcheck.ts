import useConfig from '@/hooks/useConfig';
import { useIsUserAuthenticated } from '@/hooks/useIsUserAuthenticated';
import { Healtcheck, HealthcheckStatus } from '@/types/healthcheck';
import { httpClient } from '@/utils/httpClient';
import { useQuery } from '@tanstack/react-query';
import { get } from 'lodash';
import { useEffect, useState } from 'react';

const getHealthcheck = async (): Promise<boolean> => {
  const res = await httpClient.get('/web/health');

  const healthcheck: Healtcheck = {
    status: get(res.data, 'status', HealthcheckStatus.ERROR) as HealthcheckStatus,
  };

  if (healthcheck.status !== HealthcheckStatus.HEALTHY) {
    return Promise.reject(new Error('Healthcheck failed'));
  }

  return Promise.resolve(true);
};

/**
 * useHealthcheck hook to check if the backend is online
 * @returns boolean
 */
export const useHealthcheck = (): boolean => {
  const config = useConfig();
  const isUserAuthenticated = useIsUserAuthenticated();
  const [isOnline, setIsOnline] = useState<boolean>(true);

  const { isError, isSuccess, isFetching } = useQuery<boolean, Error>({
    queryKey: ['healthcheck'],
    queryFn: () => getHealthcheck(),
    refetchInterval: () => (isOnline ? parseInt(config.HEALTHCHECK_INTERVAL) : 5000), // Will check every 30 seconds if online, otherwise every 5 seconds
    initialData: true,
    retry: 3,
    retryDelay: 1000,
    enabled: !!isUserAuthenticated && !!config.APP_URL,
  });

  useEffect(() => {
    // Sets current server status based on healthcheck request response
    if (!isFetching) setIsOnline(isSuccess && !isError);
  }, [isSuccess, isError, isFetching]);

  return isOnline;
};
