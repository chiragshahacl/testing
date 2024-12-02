import {
  DeviceAlert,
  PatientAlerts,
  ServerAlert,
  ServerSidePatientAlert,
  VitalsAlert,
} from '@/types/alerts';
import { BedType, ServerBed } from '@/types/bed';
import { AssignBedGroupData, GroupType, ServerGroup } from '@/types/group';
import { EHRPatientType, ServerEHRPatient } from '@/types/patient';
import { SENSOR_TYPES } from '@/types/sensor';
import { getAlertTypeByCode, getDeviceAlert } from '@/utils/alertUtils';
import { httpClient } from '@/utils/httpClient';
import { ALERT_TYPES, SUPPORTED_ALERT_CODES } from '@/utils/metricCodes';

/* ------- BEDS API ------- */

export const parseServerBedData = (bedsData: ServerBed[] = []): BedType[] => {
  return bedsData.map((bed) => {
    const patient = bed.patient
      ? {
          patientId: bed.patient.id,
          patientPrimaryIdentifier: bed.patient.primaryIdentifier,
          patientFirstName: bed.patient.givenName,
          patientLastName: bed.patient.familyName,
          patientGender: bed.patient.gender,
          patientDob: bed.patient.birthDate,
        }
      : undefined;

    const encounter = bed.encounter
      ? {
          patientId: bed.encounter.subjectId,
          patientMonitorId: bed.encounter.deviceId,
          createdAt: bed.encounter.createdAt,
          status: bed.encounter.status,
          startTime: bed.encounter.startTime,
          endTime: bed.encounter.endTime,
        }
      : undefined;

    return {
      id: bed.id,
      bedNo: bed.name,
      patient,
      encounter,
    };
  });
};

/* ------- GROUPS API ------- */

export const parseServerGroupData = (groupsData: ServerGroup[] = []) => {
  const res: GroupType[] = [];
  groupsData.forEach((group) => {
    const beds = parseServerBedData(group.beds);
    res.push({
      id: group.id,
      name: group.name,
      description: group.description,
      beds,
    });
  });
  return res;
};

export const assignBedsToGroupsBatch = async (groups: GroupType[]) => {
  /*
  data sample:
  {
    groups: [{name: 'Group 1', beds: [{id: '1', bedNo: '1'}]}]
  }
  */
  const groupsData: AssignBedGroupData[] = [];
  groups.forEach((group) => {
    const bedIds = group.beds.map((bed: BedType) => bed.id);
    groupsData.push({
      // eslint-disable-next-line camelcase
      group_id: group.id,
      // eslint-disable-next-line camelcase
      bed_ids: bedIds,
    });
  });
  const res = await httpClient.put('/web/bed-group/beds/batch', {
    resources: groupsData,
  });
  return res;
};

export const deleteGroupsBatch = async (groupsToDelete: string[]) => {
  /*
  data sample:
  {
    groups: ['1234-5678-9012', '9876-5432-1098']
  }
  */
  const res = await httpClient.delete('/web/bed-group/batch', {
    // eslint-disable-next-line camelcase
    data: { group_ids: groupsToDelete },
  });
  return res;
};

const parsePatientSingleAlertData = (rawAlert: ServerAlert): VitalsAlert | DeviceAlert => {
  const type = getAlertTypeByCode(rawAlert.code) as ALERT_TYPES; // Supported alert codes filtered prior to this
  return {
    type,
    id: rawAlert.id,
    code: rawAlert.code,
    deviceCode: rawAlert.deviceCode,
    priority: rawAlert.valueText,
    timestamp: rawAlert.effectiveDt,
    acknowledged: false,
    waveformMessage:
      type === ALERT_TYPES.DEVICE
        ? getDeviceAlert(rawAlert.code, rawAlert.deviceCode as SENSOR_TYPES)?.waveformMessage
        : undefined,
  };
};

const parsePatientAlertsData = (rawAlerts: ServerSidePatientAlert): PatientAlerts => ({
  patientId: rawAlerts.primaryIdentifier,
  alerts: rawAlerts.alerts
    .filter((alert) => SUPPORTED_ALERT_CODES.includes(alert.code))
    .map(parsePatientSingleAlertData),
});

export const parseGroupPatientsAlerts = (
  patientAlerts: ServerSidePatientAlert[]
): PatientAlerts[] => patientAlerts.map(parsePatientAlertsData);

/* ----- EHR Patient Assign ----- */

const parseSingleEHRPatientData = (ehrFoundPatient: ServerEHRPatient): EHRPatientType => ({
  patientPrimaryIdentifier: ehrFoundPatient.patientIdentifiers[0],
  firstName: ehrFoundPatient.givenName,
  lastName: ehrFoundPatient.familyName,
  dob: ehrFoundPatient.birthDate,
  sex: ehrFoundPatient.gender,
});

export const parseEHRPatientsData = (ehrFoundPatients: ServerEHRPatient[]): EHRPatientType[] =>
  ehrFoundPatients.map(parseSingleEHRPatientData);
