import { EncounterStatus } from './encounters';

export interface BedType {
  id: string;
  monitorId?: string;
  bedNo: string;
  patient?: {
    patientId: string;
    patientPrimaryIdentifier: string;
    patientFirstName?: string;
    patientLastName?: string;
    patientGender?: string;
    patientDob?: string;
  };
  encounter?: {
    patientId: string;
    patientMonitorId: string;
    createdAt: string;
    status: EncounterStatus;
    startTime?: string | null;
    endTime?: string | null;
  };
}

export interface ServerBed {
  id: string;
  name: string;
  patient?: {
    id: string;
    primaryIdentifier: string;
    givenName?: string;
    familyName?: string;
    gender?: string;
    birthDate?: string;
  };
  encounter?: {
    subjectId: string;
    deviceId: string;
    createdAt: string;
    status: EncounterStatus;
    startTime?: string;
    endTime?: string;
  };
}

export interface NewBedType {
  name: string;
}

export type DeleteBedType = string;
