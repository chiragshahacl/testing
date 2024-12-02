import PatientInfoTab from '@/app/(authenticated)/home/details/Tabs/PatientInformationTab';
import VitalManagementTab from '@/app/(authenticated)/home/details/Tabs/VitalsManagementTab';
import VitalsTab from '@/app/(authenticated)/home/details/Tabs/VitalsTab';
import { StyledTab, StyledTabs } from '@/components/tabs/StyledTabs';
import { DeviceAlert, VitalsAlert } from '@/types/alerts';
import { BedType } from '@/types/bed';
import { Metrics } from '@/types/metrics';
import { DisplayVitalsRange } from '@/types/patientMonitor';
import { Sensor } from '@/types/sensor';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import moment from 'moment';
import { XyDataSeries } from 'scichart/Charting/Model/XyDataSeries';
import AlarmHistoryTab from './AlarmHistoryTab';

type TabId = 'vitals' | 'patient_info' | 'vital_management' | 'alarm_history';

type TabType = {
  id: TabId;
  label: string;
};

const TABS: TabType[] = [
  {
    id: 'vitals',
    label: 'VITALS',
  },
  {
    id: 'patient_info',
    label: 'PATIENT INFO',
  },
  {
    id: 'vital_management',
    label: 'ALARM LIMITS',
  },
  {
    id: 'alarm_history',
    label: 'ALARM HISTORY',
  },
].filter((tab) => tab !== null) as TabType[];

type TabPanelProps = {
  metrics: Metrics;
  selectedBed: BedType;
  selectedBedGraphsWithData: Array<string>;
  selectedTab: string | null;
  activeSensors: Sensor[];
  isLoading: boolean;
  alertThresholds: Record<string, DisplayVitalsRange>;
  onTabSelected: (newTab: string) => void;
  sendNewDataSeries: (elementId: string, dataSeries?: XyDataSeries) => void;
  deviceAlerts: DeviceAlert[];
  vitalsAlerts: VitalsAlert[];
  hasActivePatientSession: boolean;
};

const TabPanel = ({
  selectedTab = TABS[0].id,
  onTabSelected,
  selectedBed,
  selectedBedGraphsWithData,
  metrics,
  sendNewDataSeries,
  activeSensors,
  isLoading,
  alertThresholds,
  hasActivePatientSession,
  vitalsAlerts,
  deviceAlerts,
}: TabPanelProps) => {
  const tab = selectedTab || TABS[0].id;

  const getActiveTab = () => {
    switch (tab) {
      case 'vitals':
        return (
          <VitalsTab
            selectedBed={selectedBed}
            hasActivePatientSession={hasActivePatientSession}
            graphsWithData={selectedBedGraphsWithData}
            metrics={metrics}
            sendNewDataSeries={sendNewDataSeries}
            vitalsAlerts={vitalsAlerts}
            deviceAlerts={deviceAlerts}
            activeSensors={activeSensors}
            isLoading={isLoading}
            alertThresholds={alertThresholds}
          />
        );
      case 'vital_management':
        return <VitalManagementTab metrics={metrics} alertThresholds={alertThresholds} />;
      case 'patient_info':
        return (
          <PatientInfoTab
            id={selectedBed.patient?.patientPrimaryIdentifier || '-'}
            firstName={selectedBed?.patient?.patientFirstName || '-'}
            lastName={selectedBed?.patient?.patientLastName || '-'}
            sex={selectedBed?.patient?.patientGender || '-'}
            dob={
              selectedBed?.patient?.patientDob
                ? moment(selectedBed.patient.patientDob).format('yyyy-MM-DD')
                : '-'
            }
          />
        );
      case 'alarm_history':
        return <AlarmHistoryTab patientId={selectedBed.patient?.patientId || ''} />;
      default:
        return null;
    }
  };

  return (
    <Grid display='flex' flexDirection='column' height={771}>
      <StyledTabs
        value={tab}
        label={TABS.find((t) => tab === t.id)?.label || ''}
        onChange={(_, newValue) => {
          onTabSelected(newValue);
        }}
      >
        {TABS.map((tab) => (
          <StyledTab
            key={`tab_${tab.id}`}
            data-testid={tab.label}
            label={tab.label}
            value={tab.id}
          />
        ))}
      </StyledTabs>
      <Box height='2px' sx={{ backgroundColor: 'secondary.main', marginTop: '-2px' }} />
      {getActiveTab()}
    </Grid>
  );
};

export default TabPanel;
