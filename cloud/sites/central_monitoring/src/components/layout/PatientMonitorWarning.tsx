import Typography from '@mui/material/Typography';
import { alpha } from '@mui/material/styles';
import { AlertIcon } from '../icons/AlertIcon';
import { get } from 'lodash';
import { StyledChip } from '@/styles/StyledComponents';
import { useMemo } from 'react';
import usePatientData from '@/hooks/usePatientsData';
import { usePatientMonitors } from '@/api/usePatientMonitors';
import { BedsDisplayGroup } from '@/types/patientMonitor';
import moment from 'moment';

const PatientMonitorWarning = (): JSX.Element => {
  const { bedsDisplayGroups } = usePatientData();

  const patientMonitors = usePatientMonitors();

  const TIME_INTERVAL = 20000;

  const showPatientMonitorWarning = useMemo(() => {
    let allBedsOnDisplay: string[] = [];
    bedsDisplayGroups.forEach((displayGroup: BedsDisplayGroup) => {
      if (displayGroup && displayGroup.timestamp + TIME_INTERVAL >= moment.now()) {
        allBedsOnDisplay = [...allBedsOnDisplay, ...displayGroup.beds];
      }
    });

    let allMonitorsAreDisplayed = true;
    patientMonitors.data?.forEach((monitor) => {
      if (!monitor.assignedBedId) {
        allMonitorsAreDisplayed = false;
      } else if (allBedsOnDisplay.indexOf(monitor.assignedBedId) < 0) {
        allMonitorsAreDisplayed = false;
      }
    });

    return !allMonitorsAreDisplayed;
  }, [bedsDisplayGroups, patientMonitors.data]);

  return (
    <StyledChip
      hidden={!showPatientMonitorWarning}
      display='flex'
      flexDirection='row'
      sx={{
        backgroundColor: (theme) => alpha(get(theme.palette, 'alert.medium', '#F6C905'), 0.25),
      }}
    >
      <AlertIcon />
      <Typography variant='caption'>
        Not all patient monitors are displayed. Please check group management settings.
      </Typography>
    </StyledChip>
  );
};

export default PatientMonitorWarning;
