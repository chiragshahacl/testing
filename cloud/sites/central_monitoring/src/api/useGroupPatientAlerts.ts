import { PatientAlerts, ServerSidePatientAlert } from '@/types/alerts';
import { httpClient } from '@/utils/httpClient';
import { useQuery } from '@tanstack/react-query';
import { parseGroupPatientsAlerts } from './managementApi';
import { get } from 'lodash';

const getBedGroupsVitalsAlerts = async (groupId: string, signal?: AbortSignal) => {
  const res = await httpClient<ServerSidePatientAlert[]>(`/web/bed-group/${groupId}/alerts`, {
    signal,
  });
  return parseGroupPatientsAlerts(get(res.data, 'resources', []));
};

const defaultBedGroupsVitalsAlertsData: PatientAlerts[] = [];

export const useBedGroupVitalsAlerts = (groupId: string) => {
  const { data, ...rest } = useQuery({
    queryKey: ['bed-group-vitals-alert', groupId],
    queryFn: ({ signal }) => getBedGroupsVitalsAlerts(groupId, signal),
    enabled: !!groupId,
    placeholderData: defaultBedGroupsVitalsAlertsData,
  });

  return { data: data || defaultBedGroupsVitalsAlertsData, ...rest };
};
