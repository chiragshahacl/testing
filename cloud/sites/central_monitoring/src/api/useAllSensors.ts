import { SensorQueryReturn, ServerSideSensor } from '@/types/sensor';
import { httpClient } from '@/utils/httpClient';
import { useQuery } from '@tanstack/react-query';
import { parseServerSensors } from './deviceApi';
import { get } from 'lodash';

const getAllSensors = async (
  signal: AbortSignal | undefined,
  bedGroup?: string
): Promise<SensorQueryReturn> => {
  const res = await httpClient<ServerSideSensor[]>('/web/device', {
    signal,
    params: {
      isGateway: false,
      bedGroup,
    },
  });
  return parseServerSensors(get(res.data, 'resources', []));
};

const emptySensorsData: SensorQueryReturn = { sensors: [], alertsPerMonitor: {} };

export const useAllSensors = (groupId?: string) => {
  const { data, ...rest } = useQuery<SensorQueryReturn, Error>({
    queryKey: ['all-sensors', groupId],
    queryFn: ({ signal }) => getAllSensors(signal, groupId),
    enabled: !!groupId,
    placeholderData: emptySensorsData,
  });

  return { data: data || emptySensorsData, ...rest };
};
