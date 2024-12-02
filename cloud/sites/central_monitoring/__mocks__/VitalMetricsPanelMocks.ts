import { POSITION_TYPES, RANGES_CODES } from '@/utils/metricCodes';

export const metricsMock = {
  dia: { value: 80, unit: 'mmHg' },
  sys: { value: 120, unit: 'mmHg' },
  pulse: { value: 100, unit: 'bpm' },
  bodyTemp: { value: 99.0, unit: '°F' },
  limbTemp: { value: 99.9, unit: '°F' },
  chestTemp: { value: 99.8, unit: '°F' },
  map: { value: 130, unit: '' },
  falls: { value: 0, unit: '' },
  positionDuration: { value: 35, unit: '' },
  position: { value: POSITION_TYPES.SUPINE, unit: '' },
  bodyAngle: { value: 40, unit: '' },
};

export const alertThresholdsMock = {
  [RANGES_CODES.HR]: { lowerLimit: '45', upperLimit: '120' },
  [RANGES_CODES.RR]: { lowerLimit: '5', upperLimit: '30' },
  [RANGES_CODES.SPO2]: { lowerLimit: '85', upperLimit: '100' },
  [RANGES_CODES.SYS]: { lowerLimit: '90', upperLimit: '160' },
  [RANGES_CODES.DIA]: { lowerLimit: '50', upperLimit: '110' },
  [RANGES_CODES.TEMPERATURE_SKIN]: { lowerLimit: '93.2', upperLimit: '102.2' },
  [RANGES_CODES.TEMPERATURE_BODY]: { lowerLimit: '93.2', upperLimit: '102.2' },
  [RANGES_CODES.POSITION_DURATION]: { lowerLimit: 'null', upperLimit: '120' },
  [RANGES_CODES.PR]: { lowerLimit: '45', upperLimit: '120' },
};
