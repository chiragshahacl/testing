import { RuntimeConfig, getCachedRuntimeConfig } from '@/utils/runtime';

const useConfig = (): RuntimeConfig => {
  return getCachedRuntimeConfig();
};

export default useConfig;
