import { padStart } from 'lodash';
import moment, { Moment } from 'moment';
import momentTimezone from 'moment-timezone';

const SECONDS_AGO_TEXT = 'Just now';

export const setupMoment = () => {
  moment.updateLocale('en', {
    relativeTime: {
      future: (relTime: string) =>
        relTime === SECONDS_AGO_TEXT ? SECONDS_AGO_TEXT : `in ${relTime}`,
      past: (relTime: string) =>
        relTime === SECONDS_AGO_TEXT ? SECONDS_AGO_TEXT : `${relTime} ago`,
      s: SECONDS_AGO_TEXT,
      ss: SECONDS_AGO_TEXT,
      m: '1 min',
      mm: '%d mins',
      h: '1 hour',
      hh: '%d hours',
      d: '1 day',
      dd: '%d days',
      w: '1 week',
      ww: '%d weeks',
      M: '1 month',
      MM: '%d months',
      y: '1 year',
      yy: '%d years',
    },
  });
};

const CHECK_NUMBER_REGEX = /^\d+\.?\d*$/;

export const parseMoment = (timestamp: number | string): Moment => {
  const isNumber = typeof timestamp === 'number' ? true : CHECK_NUMBER_REGEX.exec(timestamp);
  return isNumber
    ? momentTimezone.tz(parseFloat(timestamp as string), 'UTC')
    : momentTimezone.tz(timestamp, 'UTC');
};

const milisecondsInAMinute = 1000 * 60;
const milisecondsInAnHour = milisecondsInAMinute * 60;
const milisecondsInADay = milisecondsInAnHour * 24;

export const timeFromNow = (timestamp: string) => {
  const diff = moment().diff(parseMoment(timestamp));
  if (diff > milisecondsInADay) {
    if (diff > milisecondsInADay * 2) return `${Math.floor(diff / milisecondsInADay)} days ago`;
    else return '1 day ago';
  } else if (diff > milisecondsInAnHour) {
    if (diff > milisecondsInAnHour * 2)
      return `${Math.floor(diff / milisecondsInAnHour)} hours ago`;
    else return '1 hour ago';
  } else if (diff > milisecondsInAMinute) {
    if (diff > milisecondsInAMinute * 2)
      return `${Math.floor(diff / milisecondsInAMinute)} minutes ago`;
    else return '1 minute ago';
  }
  return 'Just now';
};

export const momentDurationToHourMinutesSeconds = (momentDuration: moment.Duration) => {
  const hours = padStart(momentDuration.hours().toString(), 2, '0');
  const minutes = padStart(momentDuration.minutes().toString(), 2, '0');
  const seconds = padStart(momentDuration.seconds().toString(), 2, '0');
  return `${hours}:${minutes}:${seconds}`;
};
