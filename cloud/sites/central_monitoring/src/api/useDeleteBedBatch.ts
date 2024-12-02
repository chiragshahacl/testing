import { httpClient } from '@/utils/httpClient';
import { useMutation } from '@tanstack/react-query';

const deleteBedsBatch = async (bedIds: string[]) => {
  return await httpClient.delete('web/bed/batch', {
    data: {
      // eslint-disable-next-line camelcase
      bed_ids: bedIds,
    },
  });
};

export const useDeleteBedBatch = () => {
  return useMutation({
    mutationKey: ['deleteBedBatch'],
    mutationFn: deleteBedsBatch,
  });
};
