import { POSITION_TYPES, RANGES_CODES } from '@/utils/metricCodes';

export const metricsMock = {
  hr: { value: 60, unit: 'bpm' },
  spo2: { value: 98, unit: '%' },
  rrMetric: { value: 13, unit: 'brpm' },
  dia: { value: 80, unit: 'mmHg' },
  sys: { value: 120, unit: 'mmHg' },
  pi: { value: 15, unit: '%' },
  pr: { value: 64, unit: 'bpm' },
  pulse: { value: 100, unit: 'bpm' },
  bodyTemp: { value: 99.0, unit: '°F' },
  limbTemp: { value: 99.9, unit: '°F' },
  chestTemp: { value: 99.8, unit: '°F' },
  falls: { value: 0, unit: '' },
  positionDuration: { value: 35, unit: '' },
  position: { value: POSITION_TYPES.SUPINE, unit: '' },
};

export const alertThresholdsMock = {
  [RANGES_CODES.HR]: {
    upperLimit: '120',
    lowerLimit: '45',
  },
  [RANGES_CODES.SPO2]: {
    upperLimit: '100',
    lowerLimit: '85',
  },
  [RANGES_CODES.RR]: {
    upperLimit: '30',
    lowerLimit: '5',
  },
  [RANGES_CODES.SYS]: {
    upperLimit: '160',
    lowerLimit: '90',
  },
  [RANGES_CODES.DIA]: {
    upperLimit: '111',
    lowerLimit: '50',
  },
  [RANGES_CODES.TEMPERATURE_BODY]: {
    upperLimit: '109',
    lowerLimit: '50',
  },
  [RANGES_CODES.TEMPERATURE_SKIN]: {
    upperLimit: '109',
    lowerLimit: '50',
  },
  [RANGES_CODES.PR]: {
    lowerLimit: '55',
    upperLimit: '110',
  },
};
