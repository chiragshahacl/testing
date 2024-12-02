import { BedMonitorAssociation } from '@/types/patientMonitor';
import { httpClient } from '@/utils/httpClient';
import { useMutation } from '@tanstack/react-query';

const assignBedToMonitors = async (associations: BedMonitorAssociation[]) => {
  return await httpClient.put('/web/device/bed/batch', {
    associations,
  });
};

export const useAssignBedToMonitor = () => {
  return useMutation({
    mutationFn: (associations: BedMonitorAssociation[]) => assignBedToMonitors(associations),
    mutationKey: ['assign-bed-to-monitor'],
  });
};
