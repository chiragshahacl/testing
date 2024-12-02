import { HR_TEXT_COLOR, RR_TEXT_COLOR, SPO_TEXT_COLOR } from '@/constants';
import theme from '@/theme/theme';
import { ChartLocation, ChartType, ECGDisplayConfig } from '@/types/charts';
import { get } from 'lodash';
import { XyDataSeries } from 'scichart';
import { WS_CODES } from './metricCodes';
import { Sensor, SENSOR_TYPES } from '@/types/sensor';

const ECGDisplayConfigs: Record<string, ECGDisplayConfig> = {
  default: {
    pointsPerLoop: {
      [ChartLocation.MULTI_PATIENT_SINGLE_COLUMN]: 3927, // TODO: Update with correct amount of points
      [ChartLocation.MULTI_PATIENT_DOUBLE_COLUMN]: 3927, // TODO: Update with correct amount of points
      [ChartLocation.DETAILS]: 3927,
    },
  },
};

const PLETHDisplayConfigs: Partial<Record<SENSOR_TYPES, number>> = {
  [SENSOR_TYPES.LIMB]: 982,
  [SENSOR_TYPES.NONIN]: 1150,
};

export const POINTS_LOOP_PER_GRAPH: Record<string, number> = {
  [ChartType.RR]: 1596,
};

/**
 * Returns the ChartType associated with the vitals code received. Null if
 * does not correspond to any chart
 */
export const transformWsCodeToChartType = (code: string) => {
  switch (code) {
    case WS_CODES.ECG:
      return ChartType.ECG;
    case WS_CODES.PLETH:
      return ChartType.PLETH;
    case WS_CODES.RR:
      return ChartType.RR;
    default:
      return null;
  }
};

/**
 * Returns which are the next points in a graph that should be drawn in (xArr), and which are the
 * next points in the graph that should be erased (xPlusGapArr)
 */
export const getValuesFromData = (xIndex: number, step: number, pointsLoop: number) => {
  const xArr: number[] = [];
  const xPlusGapArr: number[] = [];
  const gapPoints = Math.floor(pointsLoop / 15);
  for (let i = 0; i < step; i++) {
    const x = (xIndex + i) % pointsLoop;
    const xPlusGap = (xIndex + i + gapPoints) % pointsLoop;
    xArr.push(x);
    xPlusGapArr.push(xPlusGap);
  }
  return {
    xArr,
    xPlusGapArr,
  };
};

/**
 * Updates the value of a single point in an XyDataSeries, and removes the value
 * of another point (xPlusGap)
 */
export const updateSinglePoint = (
  sample: number | null,
  dataSeries: XyDataSeries,
  xValue: number,
  xPlusGap: number
) => {
  const { min: minRange, max: maxRange } = dataSeries.getXRange();
  if (xValue >= minRange && xValue <= maxRange) {
    if (typeof sample === 'number') {
      dataSeries.update(xValue, sample);
    } else {
      dataSeries.update(xValue, NaN);
    }
  }
  if (xPlusGap >= minRange && xPlusGap <= maxRange) {
    dataSeries.update(xPlusGap, NaN);
  }
};

/**
 * Updates multiple points in an XyDataSeries, and removes the same amount of points
 */
export const updateDataseries = (
  samples: (number | null)[],
  dataSeries: XyDataSeries,
  xArr: number[],
  xPlusGapArr: number[]
) => {
  if (dataSeries) {
    for (let i = 0; i < samples.length; i++) {
      updateSinglePoint(samples[i], dataSeries, xArr[i], xPlusGapArr[i]);
    }
  }
};

/**
 * Returns the color that should be used for graphing depending on which
 * vital metric the chart is for
 */
export const getChartColor = (chartType?: ChartType) => {
  if (chartType === ChartType.PLETH) return get(theme.palette, SPO_TEXT_COLOR, '#57C4E8');
  if (chartType === ChartType.RR) return get(theme.palette, RR_TEXT_COLOR, '#CDE8C1');
  return get(theme.palette, HR_TEXT_COLOR, '#00CC6A');
};

/**
 * Returns the amounts of points that should be used per loop of any graph,
 * depending on which type of graph it is, and for ECG cases, where it's
 * displayed and optionally for which monitor
 */
export const getPointsLoopPerGraph = (
  chartType: ChartType,
  location: ChartLocation,
  sensor?: SENSOR_TYPES,
  monitor?: string
): number => {
  if (chartType === ChartType.ECG) return getECGGraphsPointsPerLoop(location, monitor);
  else if (chartType === ChartType.PLETH) return getPLETHGraphsPointsPerLoop(sensor);
  else return POINTS_LOOP_PER_GRAPH[chartType];
};

/**
 * Returns the amounts of points that should be used per loop of an ECG graph,
 * depending on where it is displayed and optionally for which monitor
 */
const getECGGraphsPointsPerLoop = (location: ChartLocation, monitor?: string) => {
  const selectedConfig: ECGDisplayConfig =
    monitor && ECGDisplayConfigs[monitor]
      ? ECGDisplayConfigs[monitor]
      : ECGDisplayConfigs['default'];
  return selectedConfig.pointsPerLoop[location] ? selectedConfig.pointsPerLoop[location] : 0;
};

/**
 * Returns the amounts of points that should be used per loop of a PLETH graph,
 * depending on which sensor is sending the data
 */
const getPLETHGraphsPointsPerLoop = (sensor?: SENSOR_TYPES) => {
  if (!sensor) return 0;
  return PLETHDisplayConfigs[sensor] || 0;
};

/**
 * Returns the sensor that is in charge of sending PLETH data. Returns undefined if
 * no sensor is sending PLETH data
 */
export const getPLETHGraphRelatedSensor = (allSensors?: Sensor[]) => {
  const foundSensor = allSensors?.find(
    (sensor) => sensor.type === SENSOR_TYPES.LIMB || sensor.type === SENSOR_TYPES.NONIN
  );

  return foundSensor?.type;
};
