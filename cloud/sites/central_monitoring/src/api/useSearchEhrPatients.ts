import { httpClient } from '@/utils/httpClient';
import { get } from 'lodash';
import { parseEHRPatientsData } from './managementApi';
import { ServerEHRPatient } from '@/types/patient';
import { useQuery } from '@tanstack/react-query';
import {
  SearchByNameParams,
  SearchByIdParams,
  ServerSearchByIdParams,
  ServerSearchByNameParams,
} from '@/types/patientSearch';
import { SearchEHRPatientFullResponse } from '@/types/ehr';

const searchEhrPatients = async (
  params: ServerSearchByIdParams | ServerSearchByNameParams,
  signal?: AbortSignal
): Promise<SearchEHRPatientFullResponse> => {
  let status;
  let errorType;
  const res = await httpClient<ServerEHRPatient[]>('/web/patient/ehr', {
    params: params,
    signal,
  }).catch((e) => {
    status = get(e, 'response.status') as number | undefined;
    errorType = get(e, 'response.data.detail[0].type', '') as string;
  });
  return {
    foundPatients: parseEHRPatientsData(get(res, 'data.resources', []) as ServerEHRPatient[]),
    status,
    errorType,
  };
};

const useSearchEhrPatients = (params: SearchByNameParams | SearchByIdParams | null) => {
  const { data, refetch, error, isLoading, ...rest } = useQuery<
    SearchEHRPatientFullResponse,
    Error
  >({
    queryKey: ['search-patient-with-', params],
    queryFn: async ({ signal }) => {
      let ServerEHRparam;
      if (params && 'patientPrimaryIdentifier' in params) {
        ServerEHRparam = {
          patientIdentifier: params.patientPrimaryIdentifier,
        };
        return await searchEhrPatients(ServerEHRparam, signal);
      } else if (params && 'firstName' in params && 'lastName' in params && 'dob' in params) {
        ServerEHRparam = {
          givenName: params.firstName,
          familyName: params.lastName,
          birthDate: params.dob ? params.dob.replaceAll('-', '') : undefined,
        };
        return await searchEhrPatients(ServerEHRparam, signal);
      } else {
        throw new Error('Invalid search parameters');
      }
    },
    placeholderData: {
      foundPatients: [],
    },
    enabled: !!params,
    cacheTime: 0,
  });

  return {
    ...rest,
    foundPatients: data && data.foundPatients ? data.foundPatients : [],
    searchPatientStatus: data?.status,
    searchPatientErrorType: data?.errorType,
    searchPatient: refetch,
    searchPatientLoading: isLoading,
    searchPatientError: error,
  };
};

export default useSearchEhrPatients;
