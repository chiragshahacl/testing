import { ALERT_PRIORITY } from '@/utils/metricCodes';

export interface AudioHandlingScreen {
  screen?: string;
  timestamp?: number;
  priority?: ALERT_PRIORITY;
}
