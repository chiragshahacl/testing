import moment from 'moment';

export const checkAgeLessThanYears = (date: string, ageLimit: number): boolean => {
  const difference = moment().diff(moment(date), 'years');

  return difference < ageLimit;
};
