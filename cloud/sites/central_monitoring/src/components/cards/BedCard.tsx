import useAudioAlerts from '@/hooks/useAudioAlerts';
import usePatientData from '@/hooks/usePatientsData';
import useSensorsConnected from '@/hooks/useSensorsConnected';
import useTechnicalAlerts from '@/hooks/useTechnicalAlerts';
import { Alert, DeviceAlert, VitalsAlert } from '@/types/alerts';
import { Metrics } from '@/types/metrics';
import { DisplayVitalsRange } from '@/types/patientMonitor';
import { Sensor } from '@/types/sensor';
import {
  getHighestPriorityAlertColor,
  isMonitorNotAvailableAlertPresent,
} from '@/utils/alertUtils';
import {
  ALERT_TYPES,
  METRIC_INTERNAL_CODES,
  METRIC_VITALS_ALERTS_MAP,
  RANGES_CODES,
} from '@/utils/metricCodes';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { partition as lodashPartition } from 'lodash';
import { useMemo } from 'react';
import NumberBadge from '../NumberBadge';
import MinimizedVitalsCard from './MinimizedVitalsCard';
import { EncounterStatus } from '@/types/encounters';

interface BedCardProps {
  title: string;
  bedId: string;
  metrics?: Metrics;
  alertThresholds?: Record<string, DisplayVitalsRange>;
  alerts: Alert[];
  activeSensors: Sensor[];
  hasAssociatedMonitor?: boolean;
  encounterStatus?: EncounterStatus;
  isLoading: boolean;
}
const BedCard = ({
  title,
  bedId,
  metrics = {},
  alertThresholds = {},
  alerts,
  activeSensors,
  hasAssociatedMonitor = true,
  encounterStatus = undefined,
  isLoading = false,
}: BedCardProps) => {
  const { updateSelectedBed, selectedBed, loadingSelectedBed } = usePatientData();

  const [vitalsAlerts, deviceAlerts] = useMemo(
    () => lodashPartition(alerts, (alertObject) => alertObject.type === ALERT_TYPES.VITALS),
    [alerts]
  ) as [VitalsAlert[], DeviceAlert[]];
  const audioAlerts = useAudioAlerts(vitalsAlerts);
  const technicalAlerts = useTechnicalAlerts(deviceAlerts);

  const sensorsConnected = useSensorsConnected(activeSensors);

  const { hrAlerts, spoAlerts } = useMemo(
    () => ({
      hrAlerts: vitalsAlerts.filter((alertObj) =>
        METRIC_VITALS_ALERTS_MAP.HR.includes(alertObj.code)
      ),
      spoAlerts: vitalsAlerts.filter((alertObj) =>
        METRIC_VITALS_ALERTS_MAP.SPO.includes(alertObj.code)
      ),
    }),
    [vitalsAlerts]
  );

  return (
    <Grid
      data-testid='bed-card'
      className='bedCard'
      sx={{
        p: (theme) => theme.spacing(0, 12),
        backgroundColor:
          vitalsAlerts.length > 0
            ? 'secondary.main'
            : selectedBed?.id === bedId
            ? 'grey[900]'
            : 'primary.dark',
        ...(selectedBed?.id === bedId && { border: '2px solid #FFFFFF' }),
      }}
      onClick={() => {
        updateSelectedBed(bedId);
      }}
    >
      <Grid position='relative'>
        <Grid py={5}>
          <Typography variant='h6' overflow='hidden' whiteSpace='nowrap'>
            Bed ID {title}
          </Typography>
        </Grid>
        <Grid
          position='absolute'
          display='flex'
          top={0}
          right={0}
          flexDirection='row'
          width='50%'
          onClick={(event) => {
            event.stopPropagation();
          }}
          sx={{
            overflow: 'hidden',
            borderRadius: (theme) => theme.spacing(0, 16, 0, 0),
            mr: '-12px',
          }}
        >
          {deviceAlerts.length > 0 && (
            <Grid
              display='flex'
              flexDirection='row'
              sx={{
                backgroundColor: getHighestPriorityAlertColor(deviceAlerts),
                padding: (theme) => theme.spacing(5, 10),
              }}
              flex={1}
              justifyContent='center'
              data-testid='device-alerts'
            >
              <NumberBadge
                number={
                  isMonitorNotAvailableAlertPresent(deviceAlerts)
                    ? 1
                    : deviceAlerts.filter((alert) => !alert.acknowledged).length
                }
                color={getHighestPriorityAlertColor(deviceAlerts)}
              />
            </Grid>
          )}
          {audioAlerts.length > 0 && !isMonitorNotAvailableAlertPresent(deviceAlerts) && (
            <Grid
              display='flex'
              flexDirection='row'
              sx={{
                backgroundColor: getHighestPriorityAlertColor(audioAlerts),
                padding: (theme) => theme.spacing(5, 10),
              }}
              flex={1}
              justifyContent='center'
              data-testid='vitals-alerts'
            >
              <NumberBadge
                number={audioAlerts.filter((alert) => !alert.acknowledged).length}
                color={getHighestPriorityAlertColor(audioAlerts)}
              />
            </Grid>
          )}
        </Grid>
      </Grid>
      <MinimizedVitalsCard
        isLoading={loadingSelectedBed}
        encounterStatus={encounterStatus}
        isPatientMonitorAvailable={
          !(!hasAssociatedMonitor || isMonitorNotAvailableAlertPresent(deviceAlerts))
        }
        technicalAlerts={technicalAlerts}
        metricInfo={{
          HR: {
            limits: {
              upperLimit: alertThresholds[RANGES_CODES.HR]?.upperLimit,
              lowerLimit: alertThresholds[RANGES_CODES.HR]?.lowerLimit,
            },
            value: metrics[METRIC_INTERNAL_CODES.HR]?.value,
            isSensorConnected: !isLoading && sensorsConnected[METRIC_INTERNAL_CODES.HR],
            hasAlert: hrAlerts.length > 0,
          },
          SPO: {
            limits: {
              upperLimit: alertThresholds[RANGES_CODES.SPO2]?.upperLimit,
              lowerLimit: alertThresholds[RANGES_CODES.SPO2]?.lowerLimit,
            },
            value: metrics[METRIC_INTERNAL_CODES.SPO2]?.value,
            isSensorConnected: !isLoading && sensorsConnected[METRIC_INTERNAL_CODES.SPO2],
            hasAlert: spoAlerts.length > 0,
          },
        }}
      />
    </Grid>
  );
};

export default BedCard;
