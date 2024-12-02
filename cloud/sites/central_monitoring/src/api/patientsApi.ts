import {
  PatientSessionAlert,
  PatientType,
  ServerPatient,
  ServerSidePatientSessionAlert,
} from '@/types/patient';
import { httpClient } from '@/utils/httpClient/httpClient';
import { ALERT_PRIORITY } from '@/utils/metricCodes';

export const parsePatientsData = (patients: ServerPatient[]): PatientType[] => {
  // Currently data coming from server side is exactly as we expect it
  // Keeping the parse call just for standarization with our other flows
  return patients;
};

const parsePatientSessionAlert = (
  rawAlert: ServerSidePatientSessionAlert
): PatientSessionAlert => ({
  code: rawAlert.code,
  startTime: rawAlert.startDeterminationTime,
  endTime: rawAlert.endDeterminationTime,
  priority: rawAlert.valueText as ALERT_PRIORITY,
  devicePrimaryIdentifier: rawAlert.devicePrimaryIdentifier,
  deviceCode: rawAlert.deviceCode,
  upperLimit: rawAlert.triggerUpperLimit,
  lowerLimit: rawAlert.triggerLowerLimit,
});

export const parsePatientSessionAlerts = (
  patientSessionAlerts: ServerSidePatientSessionAlert[]
): PatientSessionAlert[] => patientSessionAlerts.map(parsePatientSessionAlert);

export const acknowledgePatientAdmissionRejection = async (patientId: string) => {
  const res = await httpClient.delete(`/web/patient/${patientId}/admission`);
  return res;
};
