import { CreateUpdateBedGroupData, GroupType, NewGroupType } from '@/types/group';
import { httpClient } from '@/utils/httpClient';

import { useMutation } from '@tanstack/react-query';

interface GroupRequestType {
  groupsToAdd: NewGroupType[];
  groupsToUpdate: GroupType[];
}

const putGroupBatch = async ({ groupsToAdd, groupsToUpdate }: GroupRequestType) => {
  const groups: CreateUpdateBedGroupData[] = [];

  groupsToAdd.forEach((group) => {
    groups.push({
      name: group.name,
    });
  });

  groupsToUpdate.forEach((group) => {
    groups.push({
      id: group.id,
      name: group.name,
    });
  });

  return await httpClient.put('/web/bed-group/batch', {
    resources: groups,
  });
};

export const useUpdateGroupBatch = () => {
  return useMutation({
    mutationKey: ['update-group-batch'],
    mutationFn: putGroupBatch,
  });
};
