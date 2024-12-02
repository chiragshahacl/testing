import { RANGES_CODES } from '@/utils/metricCodes';

export const metricsMock = {
  hr: { value: 60, unit: 'bpm' },
  spo2: { value: 98, unit: '%' },
};

export const alertThresholdsMock = {
  [RANGES_CODES.HR]: {
    upperLimit: '120',
    lowerLimit: '45',
  },
  [RANGES_CODES.SPO2]: {
    upperLimit: '101',
    lowerLimit: '85',
  },
};
