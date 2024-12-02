import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';

import Loading from '@/app/loading';
import { SIGNAL_LEVEL } from '@/components/cards/SensorCard/Signalicon';
import { LowSignalIcon, OutOfRangeIcon } from '@/components/icons/connectionSignal';
import { DeviceAlert } from '@/types/alerts';
import { SENSOR_TYPES, SensorStatus } from '@/types/sensor';
import { openSansFont } from '@/utils/fonts';
import { DEVICE_ALERT_CODES } from '@/utils/metricCodes';
import SensorAlertIcon from '../../icons/sensors/SensorAlertIcon';
import BatteryIndicator from './BatteryIndicator';
import SensorIcon from './SensorIcon';
import SignalIndicator from './SignalIndicator';

interface SensorCardProps {
  battery?: number;
  charging?: boolean;
  signal?: number;
  status?: SensorStatus;
  title: string;
  id: string;
  sensorType: SENSOR_TYPES;
  alert?: DeviceAlert;
  isLoading: boolean;
  hasSensorFailure: boolean;
  hasSensorSignalAlert: boolean;
}

const SensorCard = ({
  battery,
  charging,
  signal,
  status,
  title,
  id,
  sensorType,
  isLoading,
  hasSensorFailure,
  hasSensorSignalAlert,
  alert,
}: SensorCardProps) => {
  const hasSignal = typeof signal === 'number';
  const hasBattery = typeof battery === 'number';

  return (
    <Grid display='flex'>
      <Grid display='flex' height='100%' alignItems='center' mr={2}>
        <SensorIcon alert={alert} sensorType={sensorType} />
      </Grid>
      <Grid justifyContent='space-between' display='flex' flexDirection='column' mr={8}>
        <Typography
          variant='h6'
          sx={{
            lineHeight: '18px',
          }}
        >
          {title}
        </Typography>
        <Typography
          variant='subtitle2'
          sx={{
            fontFamily: openSansFont.style.fontFamily,
          }}
        >
          {id.length > 11 ? `${id.slice(0, 9)}...` : id}
        </Typography>
      </Grid>
      <Grid
        display='flex'
        flexDirection={hasBattery && hasSignal ? 'column' : 'row'}
        justifyContent='space-between'
        alignItems={hasBattery && hasSignal ? '' : 'center'}
        overflow='hidden'
      >
        {isLoading ? (
          <Loading height={32} size={32} thickness={2.5} />
        ) : (
          <>
            {hasSensorFailure ? (
              <SensorAlertIcon
                alertPriority={alert?.deviceCode === sensorType ? alert?.priority : undefined}
              />
            ) : (
              <Grid
                display='flex'
                flexDirection='column'
                alignSelf='flex-start'
                justifyContent='space-between'
              >
                {hasSensorSignalAlert &&
                  (alert?.code === DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT['code'] ? (
                    <OutOfRangeIcon />
                  ) : (
                    <LowSignalIcon />
                  ))}
                {!hasSensorSignalAlert && hasSignal && (
                  <SignalIndicator
                    signal={
                      status !== SensorStatus.CONNECTION_LOST ? signal : SIGNAL_LEVEL.NO_SIGNAL
                    }
                  />
                )}
                {hasBattery && (
                  <BatteryIndicator battery={battery} sensorType={sensorType} charging={charging} />
                )}
              </Grid>
            )}
          </>
        )}
      </Grid>
    </Grid>
  );
};

export default SensorCard;
