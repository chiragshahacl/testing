import { render, screen } from '@testing-library/react';

import SensorCard from '@/components/cards/SensorCard/SensorCard';
import { SENSOR_CODES, SENSOR_TYPES } from '@/types/sensor';

import { composeStories } from '@storybook/react';

import * as SensorCardStories from '@/stories/SensorCard/SensorCard.stories';
import React from 'react';

const { ChestSensorCard, ChestSensorCardIsLoading, ChestSensorCardWithSensorFailure } =
  composeStories(SensorCardStories);

describe('SensorCard', () => {
  it('renders all components', async () => {
    render(<ChestSensorCard />);

    expect(screen.getByText('ANNE Chest')).toBeInTheDocument();
    expect(screen.getByText('SEN-EM-001')).toBeInTheDocument();
    expect(screen.getByTestId(`${SENSOR_TYPES.CHEST}-sensor-icon`)).toBeInTheDocument();
  });

  it('shows alert icon if there is error', () => {
    render(<ChestSensorCardWithSensorFailure />);

    expect(screen.getByTestId('sensor-alert-icon')).toBeInTheDocument();
  });

  it('shows alert icon in signal is sensor out of range', () => {
    render(
      <SensorCard
        sensorType='chest'
        title='sensor name'
        isLoading={false}
        alert={{ code: '258098' }}
        id='12345678'
        deviceCode={SENSOR_CODES.chest}
        hasSensorFailure={false}
        hasSensorSignalAlert={true}
      />
    );

    expect(screen.getByTestId('out-of-range-icon')).toBeInTheDocument();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.3.7.7
   */
  test.each([
    SENSOR_TYPES.CHEST,
    SENSOR_TYPES.ADAM,
    SENSOR_TYPES.LIMB,
    SENSOR_TYPES.NONIN,
    SENSOR_TYPES.BP,
    SENSOR_TYPES.THERMOMETER,
  ])('renders correct sensor icon', async (sensorType) => {
    render(
      <SensorCard
        sensorType={sensorType}
        title='sensor name'
        isLoading={false}
        id='12345678'
        deviceCode={SENSOR_CODES.chest}
      />
    );

    expect(screen.getByTestId(`${sensorType}-sensor-icon`)).toBeInTheDocument();
  });

  it('shows loading while fetching connected sensors', () => {
    render(<ChestSensorCardIsLoading />);

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.3.10.3
   */
  test.each([
    {
      signal: -100,
      type: SENSOR_TYPES.NONIN,
    },
    {
      signal: -93,
      type: SENSOR_TYPES.ADAM,
    },
    {
      signal: -93,
      type: SENSOR_TYPES.LIMB,
    },
    {
      signal: -93,
      type: SENSOR_TYPES.CHEST,
    },
    {
      signal: -93,
      type: SENSOR_TYPES.NONIN,
    },
    {
      signal: -76,
      type: SENSOR_TYPES.NONIN,
    },
    {
      signal: -75,
      type: SENSOR_TYPES.NONIN,
    },
  ])('renders correct signal icon', async (condition) => {
    render(
      <SensorCard
        sensorType={condition.type}
        signal={condition.signal}
        title='sensor name'
        isLoading={false}
        id='12345678'
        deviceCode={SENSOR_CODES.chest}
      />
    );

    let signalStrengthText;
    if (condition.signal === -100) signalStrengthText = 'no';
    else if (condition.signal <= -93) signalStrengthText = 'weak';
    else if (condition.signal <= -76) signalStrengthText = 'fair';
    else signalStrengthText = 'good';

    expect(screen.getByTestId(`${signalStrengthText}-signal-icon`)).toBeInTheDocument();
  });

  /*
   * Requirement IDs: 	RQ-00022-B: SR-1.3.8.5 RQ-00022-B: SR-1.3.11.5 RQ-00022-B: SR-1.3.10.5
   */
  test.each([5, 20, 40, 60, 80, 100])('renders correct battery icon', async (battery) => {
    render(
      <SensorCard
        sensorType=''
        battery={battery}
        title='sensor name'
        isLoading={false}
        id='12345678'
        deviceCode={SENSOR_CODES.chest}
      />
    );

    let batteryText;
    if (battery <= 5) batteryText = 'empty';
    else if (battery <= 20) batteryText = 'low';
    else if (battery <= 40) batteryText = '40';
    else if (battery <= 60) batteryText = 'mid';
    else if (battery <= 80) batteryText = 'high';
    else batteryText = 'full';

    expect(screen.getByTestId(`${batteryText}-battery-icon`)).toBeInTheDocument();
  });
});
