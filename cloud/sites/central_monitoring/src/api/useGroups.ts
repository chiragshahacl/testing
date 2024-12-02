import { GroupType, ServerGroup } from '@/types/group';
import { httpClient } from '@/utils/httpClient';

import { useQuery } from '@tanstack/react-query';
import { parseServerGroupData } from './managementApi';
import { get } from 'lodash';

const getGroups = async (signal?: AbortSignal) => {
  const res = await httpClient<ServerGroup[]>('/web/bed-group', { signal });
  return parseServerGroupData(get(res.data, 'resources', []));
};

const defaultGroupsData: GroupType[] = [];

export const useGroups = () => {
  const { data, ...rest } = useQuery<GroupType[], Error>({
    queryKey: ['bed-groups'],
    queryFn: ({ signal }) => getGroups(signal),
    placeholderData: defaultGroupsData,
  });

  return { data: data || defaultGroupsData, ...rest };
};
