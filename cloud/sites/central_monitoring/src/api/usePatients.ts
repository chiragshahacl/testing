import { PatientType, ServerPatient } from '@/types/patient';
import { httpClient } from '@/utils/httpClient';

import { useQuery } from '@tanstack/react-query';
import { parsePatientsData } from './patientsApi';
import { get } from 'lodash';

const getPatients = async (signal?: AbortSignal) => {
  const res = await httpClient<ServerPatient[]>('/web/patient', { signal });
  return parsePatientsData(get(res.data, 'resources', []));
};

const defaultPatientsData: PatientType[] = [];

export const usePatients = () => {
  const { data, ...rest } = useQuery<PatientType[], Error>({
    queryKey: ['patient'],
    queryFn: ({ signal }) => getPatients(signal),
    placeholderData: defaultPatientsData,
  });

  return { data: data || defaultPatientsData, ...rest };
};
