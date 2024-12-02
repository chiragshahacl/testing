import { BedType, ServerBed } from '@/types/bed';
import { httpClient } from '@/utils/httpClient';
import { useQuery } from '@tanstack/react-query';
import { parseServerBedData } from './managementApi';
import { get } from 'lodash';

const getBeds = async (signal?: AbortSignal) => {
  const res = await httpClient<ServerBed[]>('/web/bed', { signal });
  return parseServerBedData(get(res.data, 'resources', []));
};

const defaultBedsData: BedType[] = [];

export const useBeds = () => {
  const { data, ...rest } = useQuery<BedType[], Error>({
    queryKey: ['bed'],
    queryFn: ({ signal }) => getBeds(signal),
    placeholderData: defaultBedsData,
  });

  return { data: data || defaultBedsData, ...rest };
};
