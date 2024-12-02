import { AlarmRecord } from '@/types/alerts';
import { ALERT_PRIORITY } from '@/utils/metricCodes';
import { faker } from '@faker-js/faker';
import moment from 'moment';

export const generateDataArray = (count: number): AlarmRecord[] => {
  const dataArray: AlarmRecord[] = [];

  for (let i = 0; i < count; i++) {
    const type = faker.helpers.arrayElement(['Physiological', 'Technical']);
    const date = moment().add(Math.floor(Math.random() * 30), 'days');
    const time = moment(date)
      .add(Math.floor(Math.random() * 24), 'hours')
      .toString();
    const priority = faker.helpers.enumValue(ALERT_PRIORITY);
    const message = faker.lorem.words(7);
    const duration = `${Math.round(Math.random() * 23)}:${Math.round(
      Math.random() * 59
    )}:${Math.round(Math.random() * 59)}`;

    dataArray.push({ type, date: date.toString(), time, priority, message, duration });
  }

  return dataArray;
};
