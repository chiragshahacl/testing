import * as React from 'react';
import { AlarmRecord } from '@/types/alerts';
import { useMemo } from 'react';
import { usePatientSessionAlerts } from '@/api/usePatientSessionAlerts';
import { fromSessionAlertsToAlarmRecords } from '@/utils/alertUtils';
import Loading from '@/app/loading';
import AlarmHistoryTabContent from './AlarmHistoryTabContent';

interface AlarmHistoryTabProps {
  patientId: string;
}

const AlarmHistoryTab = ({ patientId }: AlarmHistoryTabProps) => {
  const patientSessionAlerts = usePatientSessionAlerts(patientId);

  const alarmHistory: AlarmRecord[] = useMemo(
    () => fromSessionAlertsToAlarmRecords(patientSessionAlerts.data),
    [patientSessionAlerts.data]
  );
  if (patientSessionAlerts.isLoading) return <Loading />;
  return <AlarmHistoryTabContent alarmHistory={alarmHistory} />;
};

export default AlarmHistoryTab;
