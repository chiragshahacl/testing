import { openSansFont } from '@/utils/fonts';
import Grid from '@mui/material/Grid';
import { get } from 'lodash';

import BatteryMidLowIcon from '@/components/icons/remainingBattery/BatteryMidLowIcon';
import EmptyBatteryIcon from '@/components/icons/remainingBattery/EmptyBatteryIcon';
import FullBatteryIcon from '@/components/icons/remainingBattery/FullBatteryIcon';
import HighBatteryIcon from '@/components/icons/remainingBattery/HighBatteryIcon';
import LowBatteryIcon from '@/components/icons/remainingBattery/LowBatteryIcon';
import MidBatteryIcon from '@/components/icons/remainingBattery/MidBatteryIcon';
import { SENSOR_TYPES } from '@/types/sensor';
import Typography from '@mui/material/Typography';
import { SafeParser } from '@/utils/safeParser';
import ChargingEmptyBatteryIcon from '@/components/icons/remainingBattery/ChargingEmptyBatteryIcon';
import ChargingLowBatteryIcon from '@/components/icons/remainingBattery/ChargingLowBatteryIcon';
import ChargingMidBatteryIcon from '@/components/icons/remainingBattery/ChargingMidBatteryIcon';
import ChargingMidLowIcon from '@/components/icons/remainingBattery/ChargingMidLowIcon';
import ChargingFullBatteryIcon from '@/components/icons/remainingBattery/ChargingFullBatteryIcon';
import ChargingHighBatteryIcon from '@/components/icons/remainingBattery/ChargingHighBatteryIcon';

interface BatteryLevels {
  empty: number;
  low: number;
  midLow: number;
  midHigh: number;
  high: number;
}

const defaultBatteryLevels = {
  empty: 9,
  low: 20,
  midLow: 40,
  midHigh: 60,
  high: 80,
};

const batteryLevelsBySensorType: Partial<Record<SENSOR_TYPES, BatteryLevels>> = {
  [SENSOR_TYPES.BP]: {
    empty: 9,
    low: 20,
    midLow: 40,
    midHigh: 59,
    high: 79,
  },
};

interface BatteryIconProps {
  battery: number;
  sensorType: SENSOR_TYPES;
  charging?: boolean;
}

export const BatteryIcon = ({ battery, sensorType, charging = false }: BatteryIconProps) => {
  const batteryLevel = batteryLevelsBySensorType[sensorType] ?? defaultBatteryLevels;
  if (battery <= batteryLevel.empty) {
    return charging ? <ChargingEmptyBatteryIcon /> : <EmptyBatteryIcon />;
  } else if (battery <= batteryLevel.low) {
    return charging ? <ChargingLowBatteryIcon /> : <LowBatteryIcon />;
  } else if (battery <= batteryLevel.midLow) {
    return charging ? <ChargingMidLowIcon /> : <BatteryMidLowIcon />;
  } else if (battery <= batteryLevel.midHigh) {
    return charging ? <ChargingMidBatteryIcon /> : <MidBatteryIcon />;
  } else if (battery <= batteryLevel.high) {
    return charging ? <ChargingHighBatteryIcon /> : <HighBatteryIcon />;
  } else {
    return charging ? <ChargingFullBatteryIcon /> : <FullBatteryIcon />;
  }
};

interface BatteryIndicatorProps {
  battery: number;
  sensorType: SENSOR_TYPES;
  charging?: boolean;
}

const BatteryIndicator = ({ battery, sensorType, charging }: BatteryIndicatorProps) => {
  const batteryLevel = batteryLevelsBySensorType[sensorType] || defaultBatteryLevels;

  return (
    <Grid display='flex' flexDirection='row' flex={1} alignItems='center'>
      <BatteryIcon battery={battery} sensorType={sensorType} charging={charging} />
      <Typography
        sx={{
          fontFamily: openSansFont.style.fontFamily,
          fontWeight: battery <= batteryLevel.low ? 600 : 400,
          fontSize: 16,
          lineHeight: '120%',
          marginLeft: 5,
          color: (theme) =>
            battery <= batteryLevel.empty
              ? get(theme.palette, 'alert.high.main')
              : battery <= batteryLevel.low
              ? get(theme.palette, 'alert.low')
              : theme.palette.common.white,
        }}
      >
        {SafeParser.toFixed(battery, 0)}%
      </Typography>
    </Grid>
  );
};

export default BatteryIndicator;
