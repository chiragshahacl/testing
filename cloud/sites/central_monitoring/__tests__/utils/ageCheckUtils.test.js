import { checkAgeLessThanYears } from '@/utils/ageCheck';

const YearDifference = 12;

const testData = [
  { date: '2000-01-01', expectedResult: false },
  { date: '2007-12-31', expectedResult: false },
  { date: '2008-01-01', expectedResult: false },
  { date: '2008-01-02', expectedResult: true },
  { date: '2019-12-31', expectedResult: true },
];

describe('AgeCheckUtils', () => {
  test.each(testData)('detectsAgeStartOfDay', async ({ date, expectedResult }) => {
    jest.useFakeTimers().setSystemTime(new Date('2020-01-01 00:00'));
    const result = checkAgeLessThanYears(date, YearDifference);
    expect(result === expectedResult).toBeTruthy();
  });

  test.each(testData)('detectsAgeMiddleOfDay', async ({ date, expectedResult }) => {
    jest.useFakeTimers().setSystemTime(new Date('2020-01-01 12:30'));
    const result = checkAgeLessThanYears(date, YearDifference);
    expect(result === expectedResult).toBeTruthy();
  });

  test.each(testData)('detectsAgeEndOfDay', async ({ date, expectedResult }) => {
    jest.useFakeTimers().setSystemTime(new Date('2020-01-01 23:59'));
    const result = checkAgeLessThanYears(date, YearDifference);
    expect(result === expectedResult).toBeTruthy();
  });
});
