import { ERROR_VALUE, NO_ASSIGNED_VALUE } from '@/constants';
import { DisplayVitalsRange, PatientMonitor } from '@/types/patientMonitor';
import { RANGES_CODES } from './metricCodes';
import { BedType } from '@/types/bed';

/**
 * Returns the ID of the Patient Monitor assigned to a specific bed
 */
export const findAssociatedMonitor = (
  bedId: string,
  patientMonitors: PatientMonitor[],
  defaultValue = NO_ASSIGNED_VALUE
) => {
  const association = patientMonitors.find(
    (monitor: PatientMonitor) => monitor.assignedBedId === bedId
  );
  return association?.monitorId || defaultValue;
};

/**
 * Returns the vitals ranges for a specific bed, by retrieving them from PMs data
 */
export const findAssociatedMonitorRanges = (bedId: string, patientMonitors: PatientMonitor[]) => {
  const res: Record<string, DisplayVitalsRange> = {};
  Object.values(RANGES_CODES).forEach((code) => {
    res[code] = {
      lowerLimit: ERROR_VALUE,
      upperLimit: ERROR_VALUE,
      alertConditionEnabled: undefined,
    };
  });

  const associatedMonitor: PatientMonitor | undefined = patientMonitors.find(
    (monitor: PatientMonitor) => monitor.assignedBedId === bedId
  );
  if (associatedMonitor && associatedMonitor.vitalRanges) {
    associatedMonitor.vitalRanges.forEach((range) => {
      res[range.code] = {
        lowerLimit: `${range.lowerLimit}`,
        upperLimit: `${range.upperLimit}`,
        alertConditionEnabled: range.alertConditionEnabled,
      };
    });
  }
  return res;
};

/**
 * Find the patient associated with a particular bed by bedId
 */
export const findAssociatedBedPatient = (bedId: string, bedsData: BedType[]) => {
  const foundBed = bedsData.find((bed) => bed.id === bedId);
  if (foundBed) {
    return foundBed.patient;
  }
  return null;
};
