export enum ChartType {
  ECG = 'ecg',
  PLETH = 'pleth',
  RR = 'rr',
}

export enum ChartLocation {
  MULTI_PATIENT_SINGLE_COLUMN = 'MULTI_PATIENT_SINGLE_COLUMN',
  MULTI_PATIENT_DOUBLE_COLUMN = 'MULTI_PATIENT_DOUBLE_COLUMN',
  DETAILS = 'DETAILS',
}

export interface ECGDisplayConfig {
  pointsPerLoop: Record<ChartLocation, number>;
}
