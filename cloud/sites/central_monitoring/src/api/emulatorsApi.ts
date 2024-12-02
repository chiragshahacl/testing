import { Emulator, EmulatorSensor, ServerEmulator, ServerEmulatorSensor } from '@/types/emulator';

const parseEmulatorData = (rawEmulator: ServerEmulator) => {
  return {
    name: rawEmulator.name,
    currentMode: rawEmulator.current_mode,
    modes: rawEmulator.emulation_modes,
  };
};

const parseEmulatorsData = (rawEmulators: ServerEmulator[]) => {
  const res: Emulator[] = [];
  rawEmulators.forEach((rawEmulator) => {
    res.push(parseEmulatorData(rawEmulator));
  });
  return res;
};

const parseSensorData = (rawSensor: ServerEmulatorSensor) => {
  return {
    id: rawSensor.id,
    primaryIdentifier: rawSensor.primary_identifier,
    type: rawSensor.type,
    emulators: parseEmulatorsData(rawSensor.emulators),
  };
};

export const parseSensorsData = (rawSensors: ServerEmulatorSensor[]) => {
  const res: EmulatorSensor[] = [];
  rawSensors.forEach((rawSensor) => {
    res.push(parseSensorData(rawSensor));
  });
  return res;
};
