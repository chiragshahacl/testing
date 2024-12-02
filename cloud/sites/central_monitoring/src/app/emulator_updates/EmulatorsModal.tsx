import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import { styled } from '@mui/material/styles';
import { useEffect, useState } from 'react';

import ModalContainer from '@/components/modals/container/ModalContainer';
import { Emulator, EmulatorSensor } from '@/types/emulator';
import { PatientType } from '@/types/patient';
import { get } from 'lodash';
import Loading from '../loading';
import { SensorCardList } from './SensorCardList';

const SensorsContainer = styled(Box)(() => ({
  display: 'flex',
  marginTop: '20px',
  flexWrap: 'wrap',
  overflowY: 'scroll',
  height: '85%',
}));

const SaveButton = styled(Button)(() => ({
  border: 'white 1px solid',
  marginTop: '20px',
  width: 'fit-content',
  alignSelf: 'center',
  padding: '5px 20px',
}));

interface EmulatorsModalProps {
  isOpen: boolean;
  onClose: () => void;
  isLoading: boolean;
  onSave: (newModes: Record<string, Record<string, string>>) => void;
  patient: PatientType | null;
  sensors?: EmulatorSensor[];
}

const EmulatorsModal = ({
  isOpen,
  onClose,
  isLoading,
  onSave,
  patient,
  sensors = [],
}: EmulatorsModalProps) => {
  const [newModes, setNewModes] = useState<Record<string, Record<string, string>>>({});

  const onChange = (sensorId: string, emulatorName: string, mode: string) => {
    const newModesCopy = { ...newModes };
    if (!newModesCopy[sensorId]) newModesCopy[sensorId] = {};
    newModesCopy[sensorId][emulatorName] = mode;
    setNewModes(newModesCopy);
  };

  useEffect(() => {
    // Resets new modes values when there are no sensors
    if (!sensors || sensors.length === 0) {
      setNewModes({});
    }
  }, [isOpen, sensors]);

  const getEmulatorValue = (sensor: EmulatorSensor, emulator: Emulator): string => {
    return get(newModes, `${sensor.id}.${emulator.name}`, emulator.currentMode) as string;
  };

  return (
    <ModalContainer
      modalHidden={!isOpen || !patient}
      onClose={onClose}
      headerTitle={`${patient?.givenName || ''} ${patient?.familyName || ''}`}
    >
      {isLoading ? (
        <Box display='flex' width='100%' height='100%' alignContent='center' flexWrap='wrap'>
          <Loading height={64} />
        </Box>
      ) : (
        <Box display='flex' flexDirection='column'>
          <SensorsContainer>
            <SensorCardList
              sensors={sensors}
              onChange={onChange}
              getEmulatorValue={getEmulatorValue}
            />
          </SensorsContainer>
          <SaveButton onClick={() => onSave(newModes)}>Save</SaveButton>
        </Box>
      )}
    </ModalContainer>
  );
};

export default EmulatorsModal;
