import { ServerErrorResponse } from '@/types/response';
import { httpClient } from '@/utils/httpClient';
import { useMutation } from '@tanstack/react-query';
import { AxiosResponse } from 'axios';

export type QuickAdmitRequestData = {
  bedId: string;
  firstName: string;
  lastName: string;
  dob?: string;
  sex?: string;
};

type QuickAdmitResponse = null;

const quickAdmit = async (
  data: QuickAdmitRequestData
): Promise<AxiosResponse<QuickAdmitResponse>> => {
  const requestData = {
    bedId: data.bedId,
    payload: {
      type: 'quick-admit',
      givenName: data.firstName,
      familyName: data.lastName,
      birthDate: data.dob,
      gender: data.sex,
    },
  };
  return httpClient.post('/web/patient/admission', requestData);
};

export const useQuickAdmit = () => {
  const { mutateAsync, isLoading, ...rest } = useMutation<
    AxiosResponse<QuickAdmitResponse>,
    ServerErrorResponse,
    QuickAdmitRequestData
  >({
    mutationFn: quickAdmit,
    mutationKey: ['quick-admit'],
  });
  return { quickAdmit: mutateAsync, quickAdmitLoading: isLoading, ...rest };
};
