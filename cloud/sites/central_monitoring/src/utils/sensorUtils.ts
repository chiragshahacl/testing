import { BedType } from '@/types/bed';
import { PatientPrimaryID } from '@/types/patient';
import { PatientMonitor } from '@/types/patientMonitor';
import { Sensor } from '@/types/sensor';
import { METRIC_INTERNAL_CODES, METRIC_SENSOR_MAP } from '@/utils/metricCodes';

enum BATTERY_STATUS_VALUES {
  FULL = 'Ful',
  CHARGING = 'ChB',
  DISCHARGING = 'DisChB',
  EMPTY = 'DEB',
}

/**
 * Checks if any of the active sensors handles a specific metric
 */
export const checkSensorConnection = (
  activeSensors: Sensor[],
  metric: METRIC_INTERNAL_CODES
): boolean =>
  !!METRIC_SENSOR_MAP[metric].some((sensor) =>
    activeSensors?.map(({ type }) => type).includes(sensor)
  );

/**
 * Returns an association between monitors and patients by monitor id.
 * PMs are associated with patients through beds, so it uses both PMs information
 * and beds information to get the final association
 */
export const associatePatientMonitorsWithPatientPrimaryIdentifier = (
  patientMonitors: PatientMonitor[],
  beds: BedType[]
) => {
  const monitorPatientHash: Record<string, PatientPrimaryID> = {};
  patientMonitors.forEach((patientMonitor) => {
    if (patientMonitor.assignedBedId) {
      const foundBed = beds.find((bed) => bed.id === patientMonitor.assignedBedId);
      if (foundBed?.patient?.patientPrimaryIdentifier)
        monitorPatientHash[patientMonitor.id] = foundBed.patient.patientPrimaryIdentifier;
    }
  });
  return monitorPatientHash;
};

/**
 * Returns if the battery is charging or not based on the status received
 */
export const batteryStatusToBoolean = (batteryStatus?: string | null) => {
  return batteryStatus === BATTERY_STATUS_VALUES.CHARGING;
};
