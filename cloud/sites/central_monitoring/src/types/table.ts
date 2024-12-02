import { AlarmRecord } from './alerts';

export type AlarmHistoryTableColumnData = {
  dataKey: keyof AlarmRecord;
  label: string;
  width: number;
};

export type AlarmLimitTableColumnData = {
  dataKey: 'name' | 'unit' | 'low' | 'high';
  label: string;
  width: number;
};
