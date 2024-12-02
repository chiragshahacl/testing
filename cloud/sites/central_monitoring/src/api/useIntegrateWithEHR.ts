import { EHRconfigType } from '@/types/ehr';
import { httpClient } from '@/utils/httpClient';

import { useMutation } from '@tanstack/react-query';

const integrateWithEHR = async (config: EHRconfigType) => {
  return await httpClient.put('/web/config', config);
};

export const useIntegrateWithEHR = () => {
  const { mutateAsync, ...rest } = useMutation({
    mutationKey: ['integrate-with-ehr'],
    mutationFn: integrateWithEHR,
  });

  return { integrateEHR: mutateAsync, ...rest };
};
