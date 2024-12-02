import { Emulator, EmulatorSensor } from '@/types/emulator';
import styled from '@emotion/styled';
import Box from '@mui/material/Box';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';

const EmulatorCard = styled(Box)(() => ({
  display: 'flex',
  flexDirection: 'column',
  width: '90%',
  marginLeft: '5%',
  marginTop: '10px',
}));

interface EmulatorCardListProps {
  sensor: EmulatorSensor;
  getEmulatorValue: (sensor: EmulatorSensor, emulator: Emulator) => string;
  onChange: (sensorId: string, emulatorName: string, mode: string) => void;
}
export const EmulatorCardList = ({ sensor, getEmulatorValue, onChange }: EmulatorCardListProps) => (
  <>
    {sensor.emulators.map((emulator) => (
      <>
        <EmulatorCard key={`${sensor.id}_emulator_${emulator.name}`}>
          <div>{emulator.name}</div>
          <div>Current Mode: {emulator.currentMode}</div>
          <Select
            value={getEmulatorValue(sensor, emulator)}
            onChange={(event) => {
              onChange(sensor.id, emulator.name, event.target.value);
            }}
          >
            {emulator.modes.map((mode) => (
              <MenuItem key={mode} value={mode}>
                {mode}
              </MenuItem>
            ))}
          </Select>
        </EmulatorCard>
      </>
    ))}
  </>
);
