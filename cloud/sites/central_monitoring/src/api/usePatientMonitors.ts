import { PatientMonitor, ServerSidePatientMonitor } from '@/types/patientMonitor';
import { httpClient } from '@/utils/httpClient';

import { useQuery } from '@tanstack/react-query';
import { parseServerPatientMonitors } from './deviceApi';
import { get } from 'lodash';

const getPatientMonitors = async (signal?: AbortSignal): Promise<PatientMonitor[]> => {
  const res = await httpClient<ServerSidePatientMonitor>('/web/device', {
    params: {
      isGateway: true,
    },
    signal,
  });
  return parseServerPatientMonitors(get(res.data, 'resources', []));
};

const defaultPatientMonitorsData: PatientMonitor[] = [];

export const usePatientMonitors = () => {
  const { data, ...rest } = useQuery<PatientMonitor[], Error>({
    queryKey: ['patient-monitors'],
    queryFn: ({ signal }) => getPatientMonitors(signal),
    placeholderData: defaultPatientMonitorsData,
  });

  return { data: data || defaultPatientMonitorsData, ...rest };
};
