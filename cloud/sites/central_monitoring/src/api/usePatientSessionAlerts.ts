import { PatientSessionAlert, ServerSidePatientSessionAlert } from '@/types/patient';
import { httpClient } from '@/utils/httpClient';

import { useQuery } from '@tanstack/react-query';
import { get } from 'lodash';
import { parsePatientSessionAlerts } from './patientsApi';

const getPatientSessionAlerts = async (patientId?: string, signal?: AbortSignal) => {
  if (patientId) {
    const res = await httpClient<ServerSidePatientSessionAlert[]>(
      `/web/patient/${patientId}/session/alerts`,
      {
        signal,
      }
    );
    return parsePatientSessionAlerts(get(res.data, 'resources', []));
  }
  return [];
};

export const usePatientSessionAlerts = (patientId: string) => {
  const { data, ...rest } = useQuery<PatientSessionAlert[], Error>({
    queryKey: ['patient', patientId],
    queryFn: ({ signal }) => getPatientSessionAlerts(patientId, signal),
    enabled: !!patientId,
    placeholderData: [],
  });

  return { data: data || [], ...rest };
};
