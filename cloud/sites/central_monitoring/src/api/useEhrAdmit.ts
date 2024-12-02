import { ServerErrorResponse } from '@/types/response';
import { httpClient } from '@/utils/httpClient';
import { useMutation } from '@tanstack/react-query';
import { AxiosResponse } from 'axios';

export type EHRAdmitRequestData = {
  bedId: string;
  patientPrimaryIdentifier: string;
  firstName?: string;
  lastName?: string;
  dob?: string;
  sex?: string;
};

type EHRAdmitResponse = null;

const ehrAdmit = async (data: EHRAdmitRequestData): Promise<AxiosResponse<EHRAdmitResponse>> => {
  const requestData = {
    bedId: data.bedId,
    payload: {
      type: 'ehr-search',
      patientIdentifier: data.patientPrimaryIdentifier,
      givenName: data.firstName,
      familyName: data.lastName,
      birthDate: data.dob,
      gender: data.sex,
    },
  };

  return httpClient.post('/web/patient/admission', requestData);
};

export const useEHRAdmit = () => {
  const { mutateAsync, isLoading, ...rest } = useMutation<
    AxiosResponse<EHRAdmitResponse>,
    ServerErrorResponse,
    EHRAdmitRequestData
  >({
    mutationFn: ehrAdmit,
    mutationKey: ['ehr-admit'],
  });
  return { ehrAdmit: mutateAsync, ehrAdmitLoading: isLoading, ...rest };
};
