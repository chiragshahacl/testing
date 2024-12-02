export type Metrics = Record<string, Metric>;

export enum FallState {
  DETECTED = 'DETECTED',
  NOT_DETECTED = 'NOT DETECTED',
  UNKNOWN = 'UNKNOWN',
}

export type TemperatureUnit = '°C' | '°F';
export type BloodPressureUnit = 'mmHg';
export type PulseRateUnit = 'bpm';
export type RespiratoryRateUnit = 'brpm';
export type OximeterUnit = '%';
export type PerfusionIndexUnit = '%';
export type HeartRateUnit = 'bpm';

export type Measurement = {
  value: number | string | undefined;
  upperLimit?: string;
  lowerLimit?: string;
};

export interface Metric {
  value: string | number | null;
  unit: string;
  timestamp: string;
}
