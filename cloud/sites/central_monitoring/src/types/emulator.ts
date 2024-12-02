export interface Emulator {
  name: string;
  currentMode: string;
  modes: string[];
}

export interface EmulatorSensor {
  id: string;
  primaryIdentifier: string;
  type: string;
  emulators: Emulator[];
}

export interface ServerEmulator {
  name: string;
  current_mode: string;
  emulation_modes: string[];
}

export interface ServerEmulatorSensor {
  id: string;
  primary_identifier: string;
  type: string;
  emulators: ServerEmulator[];
}

export interface EmulatorUpdateEmulatorModes {
  name: string;
  mode: string;
}

export interface EmulatorUpdatedSensorModes {
  id: string;
  emulators: EmulatorUpdateEmulatorModes[];
}
