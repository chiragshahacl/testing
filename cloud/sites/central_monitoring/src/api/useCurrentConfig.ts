import { EHRformValues, ServerConfig } from '@/types/ehr';
import { parseEhrConfig } from '@/utils/ehr';
import { httpClient } from '@/utils/httpClient';
import { useQuery } from '@tanstack/react-query';
import { get } from 'lodash';

const getCurrentConfig = async (signal?: AbortSignal) => {
  const res = await httpClient<ServerConfig[]>('/web/config', { signal });
  return parseEhrConfig(get(res.data, 'resources', []));
};

export const useCurrentConfig = () => {
  const { data, ...rest } = useQuery<EHRformValues | undefined, Error>({
    queryKey: ['get-current-config'],
    queryFn: ({ signal }) => getCurrentConfig(signal),
  });

  return { data: data, ...rest };
};
