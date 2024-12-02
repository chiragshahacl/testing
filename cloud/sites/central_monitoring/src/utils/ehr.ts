import { EHRformValues, ServerConfig } from '@/types/ehr';
import { get } from 'lodash';

export enum EHRStep {
  UNASSIGNED = 'UNASSIGNED',
  SEARCH = 'SEARCH',
  SEARCH_RESULTS = 'SEAERCH_RESULTS',
  QUICK_ADMIT = 'QUICK_ADMIT',
  CONFIRM_REQUEST = 'CONFIRM_REQUEST',
  SUBMITTED = 'SUBMITTED',
}

export const parseEhrConfig = (configs: ServerConfig[]): EHRformValues | undefined => {
  const result = configs.reduce<Record<string, string>>((acc, item) => {
    acc[item.key] = item.value;
    return acc;
  }, {});

  return {
    host: get(result, 'MLLP_HOST', ''),
    port: parseInt(get(result, 'MLLP_PORT', '0')),
    interval: parseInt(get(result, 'MLLP_EXPORT_INTERVAL_MINUTES', '1')),
  };
};

export const NAME_REGEX = /^[a-zA-Z'’\-\s]*$/;
export const NAME_FORMAT_ERROR_MESSAGE = 'Letters, apostrophes, hyphens, and spaces only';
export const DATE_FORMAT_ERROR_MESSAGE = 'Date format must be: YYYY-MM-DD';
export const DATE_FORMAT = 'YYYY-MM-DD';
