export enum HealthcheckStatus {
  HEALTHY = 'Healthy',
  ERROR = 'Error',
}

export interface Healtcheck {
  status: HealthcheckStatus;
}
