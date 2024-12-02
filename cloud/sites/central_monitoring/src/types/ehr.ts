import { EHRPatientType } from './patient';

export type EHRformValues = {
  host: string;
  port: number;
  interval: number;
};

export type EHRconfigType = {
  password: string;
  config: {
    MLLP_HOST: string;
    MLLP_PORT: number;
    MLLP_EXPORT_INTERVAL_MINUTES: number;
  };
};

export type ServerConfig = {
  key: string;
  value: string;
};

export type ServerConfigs = {
  resources: ServerConfig[];
};

export type SearchEHRPatientFullResponse = {
  foundPatients: EHRPatientType[];
  status?: number;
  errorType?: string | null;
};
