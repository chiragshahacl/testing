export const runtimeConfigStorageName = 'runtime-config';

export interface RuntimeConfig {
  APP_URL: string;
  WSS_URL?: string;
  EMULATOR_URL?: string;
  HOSPITAL_TITLE?: string;
  HOSPITAL_TZ?: string;
  MAX_NUMBER_BEDS: string;
  HEALTHCHECK_INTERVAL: string;
  SIBEL_VERSION: string;
  // TODO: remove IGNORE_BUTTERWORTH_FILTERS when ecg scale indicator has been tested
  IGNORE_BUTTERWORTH_FILTERS: string;
}

const defaultConfig: RuntimeConfig = {
  APP_URL: '',
  HEALTHCHECK_INTERVAL: '30000',
  MAX_NUMBER_BEDS: '64',
  IGNORE_BUTTERWORTH_FILTERS: '0',
  SIBEL_VERSION: 'undefined',
};

export const getCachedRuntimeConfig = (): RuntimeConfig => {
  if (!global.localStorage) {
    return defaultConfig;
  }
  const config = localStorage.getItem(runtimeConfigStorageName);
  if (!config) {
    return defaultConfig;
  }

  return { ...defaultConfig, ...JSON.parse(config) } as RuntimeConfig;
};
export const setCachedRuntimeConfig = (config: unknown) =>
  !!global.localStorage && localStorage.setItem(runtimeConfigStorageName, JSON.stringify(config));
