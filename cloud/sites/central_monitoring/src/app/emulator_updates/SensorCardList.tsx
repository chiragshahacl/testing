import { Emulator, EmulatorSensor } from '@/types/emulator';
import styled from '@emotion/styled';
import Box from '@mui/material/Box';
import { EmulatorCardList } from './EmulatorCardList';

const SensorCard = styled(Box)(() => ({
  display: 'flex',
  flexDirection: 'column',
  width: '50%',
  marginTop: '10px',
}));

interface SensorCardListProps {
  sensors: EmulatorSensor[];
  onChange: (sensorId: string, emulatorName: string, mode: string) => void;
  getEmulatorValue: (sensor: EmulatorSensor, emulator: Emulator) => string;
}

export const SensorCardList = ({ sensors, onChange, getEmulatorValue }: SensorCardListProps) => (
  <>
    {sensors.map((sensor) => (
      <SensorCard key={`sensor_${sensor.id}`}>
        <div>{`${sensor.type}: ${sensor.primaryIdentifier}`}</div>
        <EmulatorCardList sensor={sensor} onChange={onChange} getEmulatorValue={getEmulatorValue} />
      </SensorCard>
    ))}
  </>
);
