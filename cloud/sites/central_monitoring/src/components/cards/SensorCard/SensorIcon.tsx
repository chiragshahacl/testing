import { DeviceAlert } from '@/types/alerts';
import { SENSOR_TYPES } from '@/types/sensor';

import AdamSensorIcon from '@/components/icons/sensors/AdamSensorIcon';
import BPSensorIcon from '@/components/icons/sensors/BPSensorIcon';
import ChestSensorIcon from '@/components/icons/sensors/ChestSensorIcon';
import LimbSensorIcon from '@/components/icons/sensors/LimbSensorIcon';
import NoninSensorIcon from '@/components/icons/sensors/NoninSensorIcon';
import ThermometerIcon from '@/components/icons/sensors/ThermometerIcon';

interface SensorIconProps {
  alert?: DeviceAlert;
  sensorType: string;
}

const SensorIcon = ({ alert, sensorType }: SensorIconProps) => {
  const alertPriority = alert?.deviceCode === sensorType ? alert?.priority : undefined;

  switch (sensorType) {
    case SENSOR_TYPES.CHEST:
      return <ChestSensorIcon alertPriority={alertPriority} />;
    case SENSOR_TYPES.THERMOMETER:
      return <ThermometerIcon />;
    case SENSOR_TYPES.LIMB:
      return <LimbSensorIcon alertPriority={alertPriority} />;
    case SENSOR_TYPES.BP:
      return <BPSensorIcon alertPriority={alertPriority} />;
    case SENSOR_TYPES.ADAM:
      return <AdamSensorIcon alertPriority={alertPriority} />;
    case SENSOR_TYPES.NONIN:
      return <NoninSensorIcon alertPriority={alertPriority} />;
    default:
      return null;
  }
};

export default SensorIcon;
