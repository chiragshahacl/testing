import { RANGES_CODES } from '@/utils/metricCodes';

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
