/* eslint-disable camelcase */
import { BedType, ServerBed } from '@/types/bed';
import { EncounterStatus } from '@/types/encounters';
import { GroupType } from '@/types/group';
import { PatientMonitor, ServerSidePatientMonitor } from '@/types/patientMonitor';
import { SENSOR_TYPES, Sensor } from '@/types/sensor';

export const ServerSideMockBeds: ServerBed[] = [
  {
    id: 'bed_1',
    name: 'Bed 1',
    patient: {
      givenName: 'John',
      familyName: 'Doe',
      gender: 'Male',
      primaryIdentifier: 'pid1',
      id: '00000000-0000-0000-0000-000000000000',
      birthDate: '15/12/1984',
    },
  },
  {
    id: 'bed_2',
    name: 'Bed 2',
    patient: {
      givenName: 'Jane',
      familyName: 'Doe',
      gender: 'Female',
      primaryIdentifier: 'pid2',
      id: '00000000-0000-0000-0000-000000000001',
      birthDate: '25/09/1988',
    },
  },
  {
    id: 'bed_3',
    name: 'Bed 3',
    patient: {
      givenName: 'John',
      familyName: 'Doe',
      gender: 'Male',
      primaryIdentifier: 'pid3',
      id: '00000000-0000-0000-0000-000000000002',
      birthDate: '04/01/1984',
    },
  },
  {
    id: 'bed_4',
    name: 'Bed 4',
    patient: {
      givenName: 'Jane',
      familyName: 'Doe',
      gender: 'Female',
      primaryIdentifier: 'pid4',
      id: '00000000-0000-0000-0000-000000000003',
      birthDate: '03/12/1988',
    },
  },
  {
    id: 'bed_5',
    name: 'Bed 5',
    patient: {
      givenName: 'John',
      familyName: 'Doe',
      gender: 'Male',
      primaryIdentifier: 'pid5',
      id: '00000000-0000-0000-0000-000000000004',
      birthDate: '27/11/1991',
    },
  },
  {
    id: 'bed_6',
    name: 'Bed 6',
    patient: {
      givenName: 'Jane',
      familyName: 'Doe',
      gender: 'Female',
      primaryIdentifier: 'pid6',
      id: '00000000-0000-0000-0000-000000000005',
      birthDate: '13/03/1987',
    },
  },
  {
    id: 'bed_7',
    name: 'Bed 7',
    patient: {
      givenName: 'John',
      familyName: 'Doe',
      gender: 'Male',
      primaryIdentifier: 'pid7',
      id: '00000000-0000-0000-0000-000000000006',
      birthDate: '11/11/1985',
    },
  },
  {
    id: 'bed_8',
    name: 'Bed 8',
    patient: {
      givenName: 'Jane',
      familyName: 'Doe',
      gender: 'Female',
      primaryIdentifier: 'pid8',
      id: '00000000-0000-0000-0000-000000000007',
      birthDate: '22/05/1988',
    },
  },
  {
    id: 'bed_9',
    name: 'Bed 9',
    patient: {
      givenName: 'John',
      familyName: 'Doe',
      gender: 'Male',
      primaryIdentifier: 'pid9',
      id: '00000000-0000-0000-0000-000000000008',
      birthDate: '04/09/1993',
    },
  },
  {
    id: 'bed_10',
    name: 'Bed 10',
    patient: {
      givenName: 'Jane',
      familyName: 'Doe',
      gender: 'Female',
      primaryIdentifier: 'pid10',
      id: '00000000-0000-0000-0000-000000000009',
      birthDate: '11/12/1987',
    },
  },
  {
    id: 'bed_11',
    name: 'Bed 11',
    patient: {
      givenName: 'John',
      familyName: 'Doe',
      gender: 'Male',
      primaryIdentifier: 'pid11',
      id: '00000000-0000-0000-0000-00000000000a',
      birthDate: '07/06/1986',
    },
  },
  {
    id: 'bed_12',
    name: 'Bed 12',
    patient: {
      givenName: 'Jane',
      familyName: 'Doe',
      gender: 'Female',
      primaryIdentifier: 'pid12',
      id: '00000000-0000-0000-0000-00000000000b',
      birthDate: '27/05/1988',
    },
  },
  {
    id: 'bed_13',
    name: 'Bed 13',
    patient: {
      givenName: 'John',
      familyName: 'Doe',
      gender: 'Male',
      primaryIdentifier: 'pid13',
      id: '00000000-0000-0000-0000-00000000000c',
      birthDate: '21/01/1989',
    },
  },
  {
    id: 'bed_14',
    name: 'Bed 14',
    patient: {
      givenName: 'Jane',
      familyName: 'Doe',
      gender: 'Female',
      primaryIdentifier: 'pid14',
      id: '00000000-0000-0000-0000-00000000000d',
      birthDate: '01/04/1991',
    },
  },
  {
    id: 'bed_15',
    name: 'Bed 15',
    patient: {
      givenName: 'John',
      familyName: 'Doe',
      gender: 'Male',
      primaryIdentifier: 'pid15',
      id: '00000000-0000-0000-0000-00000000000e',
      birthDate: '08/08/1987',
    },
  },
  {
    id: 'bed_16',
    name: 'Bed 16',
    patient: {
      givenName: 'Jane',
      familyName: 'Doe',
      gender: 'Female',
      primaryIdentifier: 'pid16',
      id: '00000000-0000-0000-0000-00000000000f',
      birthDate: '15/12/1984',
    },
  },
];

export const MockBeds: BedType[] = [
  {
    id: 'bed_1',
    bedNo: 'Bed 1',
    patient: {
      patientFirstName: 'John',
      patientLastName: 'Doe',
      patientGender: 'Male',
      patientPrimaryIdentifier: 'pid1',
      patientId: '00000000-0000-0000-0000-000000000000',
      patientDob: '15/12/1984',
    },
    encounter: {
      patientId: '00000000-0000-0000-0000-000000000000',
      patientMonitorId: 'monitorId',
      createdAt: '12-12-2000 13:00:00',
      status: EncounterStatus.IN_PROGRESS,
      startTime: '12-12-2000 13:00:05',
      endTime: undefined,
    },
    monitorId: 'S4RJVEKVR2',
  },
  {
    id: 'bed_2',
    bedNo: 'Bed 2',
    patient: {
      patientFirstName: 'Jane',
      patientLastName: 'Doe',
      patientGender: 'Female',
      patientPrimaryIdentifier: 'pid2',
      patientId: '00000000-0000-0000-0000-000000000001',
      patientDob: '25/09/1988',
    },
    monitorId: 'OF0F4I4GGH',
  },
  {
    id: 'bed_3',
    bedNo: 'Bed 3',
    patient: {
      patientFirstName: 'John',
      patientLastName: 'Doe',
      patientGender: 'Male',
      patientPrimaryIdentifier: 'pid3',
      patientId: '00000000-0000-0000-0000-000000000002',
      patientDob: '04/01/1984',
    },
    monitorId: '4X1IVFO0N8',
  },
  {
    id: 'bed_4',
    bedNo: 'Bed 4',
    patient: {
      patientFirstName: 'Jane',
      patientLastName: 'Doe',
      patientGender: 'Female',
      patientPrimaryIdentifier: 'pid4',
      patientId: '00000000-0000-0000-0000-000000000003',
      patientDob: '03/12/1988',
    },
    monitorId: 'O2ROHQQU0H',
  },
  {
    id: 'bed_5',
    bedNo: 'Bed 5',
    patient: {
      patientFirstName: 'John',
      patientLastName: 'Doe',
      patientGender: 'Male',
      patientPrimaryIdentifier: 'pid5',
      patientId: '00000000-0000-0000-0000-000000000004',
      patientDob: '27/11/1991',
    },
    monitorId: 'EJGYOJGBHM',
  },
  {
    id: 'bed_6',
    bedNo: 'Bed 6',
    patient: {
      patientFirstName: 'Jane',
      patientLastName: 'Doe',
      patientGender: 'Female',
      patientPrimaryIdentifier: 'pid6',
      patientId: '00000000-0000-0000-0000-000000000005',
      patientDob: '13/03/1987',
    },
    monitorId: 'OIKD9XGDS1',
  },
  {
    id: 'bed_7',
    bedNo: 'Bed 7',
    patient: {
      patientFirstName: 'John',
      patientLastName: 'Doe',
      patientGender: 'Male',
      patientPrimaryIdentifier: 'pid7',
      patientId: '00000000-0000-0000-0000-000000000006',
      patientDob: '11/11/1985',
    },
    monitorId: 'NDWGTWXQAW',
  },
  {
    id: 'bed_8',
    bedNo: 'Bed 8',
    patient: {
      patientFirstName: 'Jane',
      patientLastName: 'Doe',
      patientGender: 'Female',
      patientPrimaryIdentifier: 'pid8',
      patientId: '00000000-0000-0000-0000-000000000007',
      patientDob: '22/05/1988',
    },
    monitorId: 'UC53AXZOGM',
  },
  {
    id: 'bed_9',
    bedNo: 'Bed 9',
    patient: {
      patientFirstName: 'John',
      patientLastName: 'Doe',
      patientGender: 'Male',
      patientPrimaryIdentifier: 'pid9',
      patientId: '00000000-0000-0000-0000-000000000008',
      patientDob: '04/09/1993',
    },
    monitorId: 'IHHTF8IJ49',
  },
  {
    id: 'bed_10',
    bedNo: 'Bed 10',
    patient: {
      patientFirstName: 'Jane',
      patientLastName: 'Doe',
      patientGender: 'Female',
      patientPrimaryIdentifier: 'pid10',
      patientId: '00000000-0000-0000-0000-000000000009',
      patientDob: '11/12/1987',
    },
    monitorId: '9X9ZJJLADG',
  },
  {
    id: 'bed_11',
    bedNo: 'Bed 11',
    patient: {
      patientFirstName: 'John',
      patientLastName: 'Doe',
      patientGender: 'Male',
      patientPrimaryIdentifier: 'pid11',
      patientId: '00000000-0000-0000-0000-00000000000a',
      patientDob: '07/06/1986',
    },
    monitorId: 'JEPYBUCSJP',
  },
  {
    id: 'bed_12',
    bedNo: 'Bed 12',
    patient: {
      patientFirstName: 'Jane',
      patientLastName: 'Doe',
      patientGender: 'Female',
      patientPrimaryIdentifier: 'pid12',
      patientId: '00000000-0000-0000-0000-00000000000b',
      patientDob: '27/05/1988',
    },
    monitorId: 'ECQ2PHDNWJ',
  },
  {
    id: 'bed_13',
    bedNo: 'Bed 13',
    patient: {
      patientFirstName: 'John',
      patientLastName: 'Doe',
      patientGender: 'Male',
      patientPrimaryIdentifier: 'pid13',
      patientId: '00000000-0000-0000-0000-00000000000c',
      patientDob: '21/01/1989',
    },
    monitorId: '4PO3FM9B52',
  },
  {
    id: 'bed_14',
    bedNo: 'Bed 14',
    patient: {
      patientFirstName: 'Jane',
      patientLastName: 'Doe',
      patientGender: 'Female',
      patientPrimaryIdentifier: 'pid14',
      patientId: '00000000-0000-0000-0000-00000000000d',
      patientDob: '01/04/1991',
    },
    monitorId: 'F69QWLEVP8',
  },
  {
    id: 'bed_15',
    bedNo: 'Bed 15',
    patient: {
      patientFirstName: 'John',
      patientLastName: 'Doe',
      patientGender: 'Male',
      patientPrimaryIdentifier: 'pid15',
      patientId: '00000000-0000-0000-0000-00000000000e',
      patientDob: '08/08/1987',
    },
    monitorId: '44LJGG81O7',
  },
  {
    id: 'bed_16',
    bedNo: 'Bed 16',
    patient: {
      patientFirstName: 'Jane',
      patientLastName: 'Doe',
      patientGender: 'Female',
      patientPrimaryIdentifier: 'pid16',
      patientId: '00000000-0000-0000-0000-00000000000f',
      patientDob: '15/12/1984',
    },
    monitorId: 'O08SLI8OPZ',
  },
];

export const MockGroups: GroupType[] = [
  {
    id: 'group_1',
    name: 'Group 1',
    beds: MockBeds.slice(0, 16),
  },
  {
    id: 'group_2',
    name: 'Group 2',
    beds: MockBeds.slice(0, 8),
  },
  {
    id: 'group_3',
    name: 'Group 3',
    beds: MockBeds.slice(0, 4),
  },
  {
    id: 'group_4',
    name: 'Group 4',
    beds: MockBeds.slice(0, 2),
  },
  {
    id: 'group_5',
    name: 'Group 5',
    beds: MockBeds.slice(0, 1),
  },
];

export const MockPatientMonitors: ServerSidePatientMonitor[] = [
  {
    id: 'monitor_1',
    primary_identifier: 'PM-001',
    name: 'PM-001',
    location_id: 'bed_1',
    device_code: 'Patient Monitor',
    gateway_id: null,
    alerts: [],
  },
  {
    id: 'monitor_2',
    primary_identifier: 'PM-002',
    name: 'PM-002',
    location_id: 'bed_2',
    device_code: 'Patient Monitor',
    gateway_id: null,
    alerts: [],
  },
  {
    id: 'monitor_3',
    primary_identifier: 'PM-003',
    name: 'PM-003',
    location_id: 'bed_3',
    device_code: 'Patient Monitor',
    gateway_id: null,
    alerts: [],
  },
  {
    id: 'monitor_4',
    primary_identifier: 'PM-004',
    name: 'PM-004',
    location_id: null,
    device_code: 'Patient Monitor',
    gateway_id: null,
    alerts: [],
  },
];

export const MockPatientMonitorsFE: PatientMonitor[] = [
  {
    id: 'monitor_1',
    monitorId: 'PM-001',
    assignedBedId: 'bed_1',
    deviceCode: 'Patient Monitor',
    alerts: [],
  },
  {
    id: 'monitor_2',
    monitorId: 'PM-002',
    assignedBedId: 'bed_2',
    deviceCode: 'Patient Monitor',
    alerts: [],
  },
];

export const MockDeviceAlerts = [{ id: '1', display: 'This is an alert.' }];

export const MockVitalsAlerts = [
  { id: '3', display: 'This is an alert', acknowledged: true },
  { id: '4', display: 'This is an alert' },
];

export const MockSensorReadings: Sensor[] = [
  {
    type: SENSOR_TYPES.ADAM,
    title: 'ANNE Chest',
    id: '12345674',
    primaryIdentifier: '12345674',
    patientMonitorId: 'monitor_1',
  },
  {
    type: SENSOR_TYPES.LIMB,
    title: 'ANNE Limb',
    id: '12345673',
    primaryIdentifier: '12345673',
    patientMonitorId: 'monitor_2',
  },
  {
    type: SENSOR_TYPES.BP,
    title: 'Viatom BP',
    id: '12345671',
    primaryIdentifier: '12345671',
    patientMonitorId: 'monitor_3',
  },
  {
    type: SENSOR_TYPES.THERMOMETER,
    title: 'Thermometer',
    id: '12345672',
    primaryIdentifier: '12345672',
    patientMonitorId: 'monitor_4',
  },
];
