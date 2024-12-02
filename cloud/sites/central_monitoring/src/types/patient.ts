import { ALERT_PRIORITY } from '@/utils/metricCodes';

export interface PatientType {
  id: string;
  primaryIdentifier: string;
  givenName: string;
  familyName: string;
  gender: string;
  birthDate: string;
}

export interface ServerPatient {
  id: string;
  primaryIdentifier: string;
  givenName: string;
  familyName: string;
  gender: string;
  birthDate: string;
}

export interface ServerSidePatientSessionAlert {
  code: string;
  startDeterminationTime: string;
  endDeterminationTime: string;
  valueText: string;
  devicePrimaryIdentifier: string;
  deviceCode: string;
  triggerLowerLimit?: number | null;
  triggerUpperLimit?: number | null;
}

export interface PatientSessionAlert {
  code: string;
  startTime: string;
  endTime: string;
  priority: ALERT_PRIORITY;
  devicePrimaryIdentifier: string;
  deviceCode: string;
  upperLimit?: number | null;
  lowerLimit?: number | null;
}

export interface ServerEHRPatient {
  patientIdentifiers: string[];
  givenName: string;
  familyName: string;
  birthDate?: string;
  gender?: string;
}

export interface EHRPatientType {
  firstName: string;
  lastName: string;
  dob?: string;
  patientPrimaryIdentifier: string;
  sex?: string;
}

export enum PatientGender {
  MALE = 'male',
  FEMALE = 'female',
  OTHER = 'other',
  UNKNOWN = 'unknown',
}

export type PatientPrimaryID = string;
