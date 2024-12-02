import { useAllSensors } from '@/api/useAllSensors';
import { useBeds } from '@/api/useBeds';
import { useBedGroupVitalsAlerts } from '@/api/useGroupPatientAlerts';
import { usePatientMonitors } from '@/api/usePatientMonitors';
import { MONITOR_AVAILABILITY_CHECK_INTERVAL, MONITOR_NOT_AVAILABLE_THRESHOLD } from '@/constants';
import usePatientData from '@/hooks/usePatientsData';
import useThrottledState from '@/hooks/useThrottledState';
import { Alert, PatientAlerts } from '@/types/alerts';
import { BedType } from '@/types/bed';
import { PatientPrimaryID } from '@/types/patient';
import {
  generateNewMonitorNotAvailableAlert,
  isAlertActive,
  removeAlertFromListByCode,
} from '@/utils/alertUtils';
import { ALERT_TYPES, DEVICE_ALERT_CODES } from '@/utils/metricCodes';
import { findAssociatedMonitor } from '@/utils/patientUtils';
import { associatePatientMonitorsWithPatientPrimaryIdentifier } from '@/utils/sensorUtils';
import { clone } from 'lodash';
import moment from 'moment';
import { useEffect, useRef } from 'react';

// Rate limit in milliseconds at which the alerts' state will be updated
const ALERTS_RATE_LIMIT = 150;

/**
 * @description Handles alerts for the provided group.
 * @param activeGroupId id of currently active group
 * @returns Current Alerts Data and methods for handling alerts updates. Specifically:
 * alertsByPatient - Alerts by patient id, which includes vitals and technical alerts
 * alertsByBed - Bed Specific alerts by id. Used for local Not Available alerts and technical alerts
 *    when no patient is connected.
 * postNewAlert - Adds or removes an alert
 * resetAlerts - Resets all currently stored alerts
 * refetchAlerts - Refetchs alerts from server
 */
const useAlerts = (activeGroupId: string) => {
  const { getActiveGroup, monitorsFreshDataKeepAlive } = usePatientData();
  const [alertsByPatient, setAlertsByPatient] = useThrottledState<
    Record<PatientPrimaryID, Alert[]>
  >({}, ALERTS_RATE_LIMIT);
  const [alertsByBed, setAlertsByBed] = useThrottledState<Record<string, Alert[]>>(
    {},
    ALERTS_RATE_LIMIT
  );

  const bedGroupVitalsAlerts = useBedGroupVitalsAlerts(activeGroupId);
  const patientMonitors = usePatientMonitors();
  const beds = useBeds();
  const allSensors = useAllSensors(activeGroupId);

  const currentGroupBeds = useRef<BedType[]>([]);

  const resetAlerts = () => {
    setAlertsByPatient({});
    setAlertsByBed({});
  };

  const resetAlertsForPatientByAlertType = (patientId: string, alertType: ALERT_TYPES) => {
    if (patientId) {
      setAlertsByPatient((previousAlerts) => {
        return {
          ...previousAlerts,
          [patientId]: (previousAlerts[patientId] || []).filter(
            (alert) => alert.type !== alertType
          ),
        };
      });
    }
  };

  const resetAlertsForPatient = (patientId: string) => {
    if (patientId) {
      setAlertsByPatient((previousAlerts) => {
        return { ...previousAlerts, [patientId]: [] };
      });
    }
  };

  const postNewAlert = (
    alertObject: Alert,
    patientId: PatientPrimaryID,
    shouldBeActive: boolean
  ) => {
    if (patientId) {
      setAlertsByPatient((previousAlerts) => {
        const previousPatientAlerts = previousAlerts[patientId] || [];
        const isCurrentlyActive = isAlertActive(alertObject, previousPatientAlerts);
        if (!isCurrentlyActive && shouldBeActive) {
          return { ...previousAlerts, [patientId]: [...previousPatientAlerts, alertObject] };
        } else if (isCurrentlyActive && !shouldBeActive) {
          return {
            ...previousAlerts,
            [patientId]: removeAlertFromListByCode(alertObject, previousPatientAlerts),
          };
        }

        return previousAlerts;
      });
    }
  };

  const postBedAlert = (alertObject: Alert, bedId: string, shouldBeActive: boolean) => {
    if (bedId) {
      setAlertsByBed((previousAlerts) => {
        const previousPatientAlerts = previousAlerts[bedId] || [];
        const isCurrentlyActive = isAlertActive(alertObject, previousPatientAlerts);

        if (!isCurrentlyActive && shouldBeActive) {
          return { ...previousAlerts, [bedId]: [...previousPatientAlerts, alertObject] };
        } else if (isCurrentlyActive && !shouldBeActive) {
          return {
            ...previousAlerts,
            [bedId]: removeAlertFromListByCode(alertObject, previousPatientAlerts),
          };
        }

        return previousAlerts;
      });
    }
  };

  const refetchAlerts = async () => bedGroupVitalsAlerts.refetch();

  const checkMonitorDataFreshness = (monitorId: string) =>
    moment(monitorsFreshDataKeepAlive.current[monitorId] + MONITOR_NOT_AVAILABLE_THRESHOLD).isAfter(
      moment()
    );

  const cleanBedAlerts = () => {
    const newAlertsByBed = clone(alertsByBed);
    Object.keys(alertsByBed).forEach((bedId) => {
      if (
        !beds.data.find((bed) => bed.id === bedId) ||
        !patientMonitors.data.find((monitor) => monitor.assignedBedId === bedId)
      ) {
        delete newAlertsByBed[bedId];
      }
    });
    setAlertsByBed(newAlertsByBed);
  };

  useEffect(() => {
    // Updates which alerts should exist when there is new vitals alerts information
    // retrieved from the backend
    if (bedGroupVitalsAlerts.isSuccess) {
      const patientsWithAlerts: string[] = [];
      bedGroupVitalsAlerts.data.map((patientAlert: PatientAlerts) => {
        const pid = patientAlert.patientId;
        if (pid) {
          patientsWithAlerts.push(pid);
          let alertsToRemove =
            alertsByPatient[pid]?.filter((alert) => alert.type === ALERT_TYPES.VITALS) ?? [];
          patientAlert.alerts.map((alert: Alert) => {
            postNewAlert(alert, pid, true);
            alertsToRemove = alertsToRemove.filter(
              (alertToRemove) => alertToRemove.code !== alert.code
            );
          });
          alertsToRemove.forEach((removeAlert) => {
            postNewAlert(removeAlert, pid, false);
          });
        }
      });
      Object.entries(alertsByPatient).forEach(([pid, alerts]) => {
        if (patientsWithAlerts.indexOf(pid) < 0) {
          alerts.forEach((alert) => {
            if (alert.type === ALERT_TYPES.VITALS) {
              postNewAlert(alert, pid, false);
            }
          });
        }
      });
    }
  }, [bedGroupVitalsAlerts.isSuccess, bedGroupVitalsAlerts.data]);

  useEffect(() => {
    // Removes alerts from non-existent beds/monitors when they were removed
    // according to API requests
    if (beds.data.length > 0 && patientMonitors.data.length > 0) {
      cleanBedAlerts();
    } else {
      setAlertsByBed({});
    }
  }, [beds.data, patientMonitors.data]);

  useEffect(() => {
    // Add device alerts to each patient from server data
    if (
      beds.data?.length > 0 &&
      patientMonitors.data?.length > 0 &&
      allSensors.data?.alertsPerMonitor
    ) {
      // Both sensors and monitors may have alerts
      const alertsPerMonitor = clone(allSensors.data.alertsPerMonitor);
      const monitorBedHash: Record<string, string> = {};
      patientMonitors.data?.forEach((monitor) => {
        if (monitor.assignedBedId) {
          monitorBedHash[monitor.id] = monitor.assignedBedId;
        }
        alertsPerMonitor[monitor.id] = monitor.alerts.concat(alertsPerMonitor[monitor.id] || []);
      });

      const monitorPatientHash = associatePatientMonitorsWithPatientPrimaryIdentifier(
        patientMonitors.data,
        beds.data
      );

      const previousAlertsCopy = clone(alertsByPatient);
      const previousBedAlertsCopy = clone(alertsByBed);
      Object.keys(alertsPerMonitor).forEach((patientMonitorId) => {
        const pid = monitorPatientHash[patientMonitorId];
        const bedId = monitorBedHash[patientMonitorId];
        if (pid) {
          resetAlertsForPatientByAlertType(pid, ALERT_TYPES.DEVICE);
          let alertsToRemove =
            previousAlertsCopy[pid]?.filter((alert) => alert.type === ALERT_TYPES.DEVICE) ?? [];
          alertsPerMonitor[patientMonitorId].forEach((alertObject) => {
            postNewAlert(alertObject, pid, true);
            alertsToRemove = alertsToRemove.filter(
              (alertToRemove) => alertToRemove.code !== alertObject.code
            );
          });
          alertsToRemove.forEach((removeAlert) => {
            postNewAlert(removeAlert, pid, false);
          });
        } else if (bedId) {
          let alertsToRemove =
            previousBedAlertsCopy[bedId]?.filter((alert) => alert.type === ALERT_TYPES.DEVICE) ??
            [];
          alertsPerMonitor[patientMonitorId].forEach((alertObject) => {
            const isActive = isAlertActive(alertObject, alertsByBed[bedId]);
            if (!isActive) {
              postBedAlert(alertObject, bedId, true);
            }
            alertsToRemove = alertsToRemove.filter(
              (alertToRemove) => alertToRemove.code !== alertObject.code
            );
          });
          alertsToRemove.forEach((removeAlert) => {
            postBedAlert(removeAlert, bedId, false);
          });
        }
      });
    }
  }, [beds.data, patientMonitors.data, allSensors.data]);

  useEffect(() => {
    currentGroupBeds.current = getActiveGroup().beds.map(
      ({ id }: BedType) => beds.data.find((bed: BedType) => bed.id === id) as BedType
      // It is not possible for the bed to not exist that we assigned to a group
    );
  }, [beds.data, activeGroupId, getActiveGroup]);

  useEffect(() => {
    if (getActiveGroup().beds) {
      const intervalCallback = setInterval(() => {
        // Interval for checking if any of the patient monitors seems unavailable
        currentGroupBeds.current.forEach((bed) => {
          const bedId = bed?.id;
          const monitorId = findAssociatedMonitor(bedId, patientMonitors.data);
          if (bedId && monitorId !== 'N/A') {
            let bedAlerts: Alert[] = [];
            if (alertsByBed[bedId]) bedAlerts = [...alertsByBed[bedId]];
            if (bed.patient && alertsByPatient[bed.patient.patientPrimaryIdentifier])
              bedAlerts = bedAlerts.concat(alertsByPatient[bed.patient.patientPrimaryIdentifier]);
            const monitorIsAvailable = checkMonitorDataFreshness(monitorId);
            const newMonitorNotAvailableAlert = generateNewMonitorNotAvailableAlert();
            const hasMonitorNotAvailableAlert = bedAlerts.find(
              (alert) => alert.code === DEVICE_ALERT_CODES.MONITOR_NOT_AVAILABLE_ALERT.code
            );
            // If the monitor is available remove the alert, otherwise send a new one
            if (monitorIsAvailable && hasMonitorNotAvailableAlert) {
              postBedAlert(newMonitorNotAvailableAlert, bedId, false);
            } else if (!monitorIsAvailable && !hasMonitorNotAvailableAlert) {
              postBedAlert(newMonitorNotAvailableAlert, bedId, true);
            }
          }
        });
      }, MONITOR_AVAILABILITY_CHECK_INTERVAL);
      return () => {
        clearInterval(intervalCallback);
      };
    }
  }, [beds.isSuccess, beds.data, patientMonitors.data, alertsByBed, alertsByPatient]);

  return {
    alertsByPatient,
    alertsByBed,
    resetAlerts,
    resetAlertsForPatient,
    postNewAlert,
    refetchAlerts,
  };
};

export default useAlerts;
