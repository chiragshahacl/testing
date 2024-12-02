import { BedType, NewBedType } from '@/types/bed';
import { httpClient } from '@/utils/httpClient';

import { useMutation } from '@tanstack/react-query';

export type BedRequestType = BedType | NewBedType;

const putBedBatch = async (resources: BedRequestType[]) => {
  return await httpClient.put('/web/bed/batch', {
    resources,
  });
};

const useUpdateBedBatch = () => {
  return useMutation({
    mutationKey: ['update-bed-batch'],
    mutationFn: putBedBatch,
  });
};

export { useUpdateBedBatch };
