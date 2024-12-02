import { EmulatorSensor, ServerEmulatorSensor } from '@/types/emulator';
import { emulatorClient } from '@/utils/httpClient';
import { useQuery } from '@tanstack/react-query';
import { parseSensorsData } from './emulatorsApi';
import { get } from 'lodash';

const getEmulatorSensors = async (patientPrimaryIdentifier?: string, signal?: AbortSignal) => {
  const res = await emulatorClient<ServerEmulatorSensor>('/emulator/sensor', {
    params: {
      // eslint-disable-next-line camelcase
      patient_primary_identifier: patientPrimaryIdentifier,
    },
    signal,
  });
  return parseSensorsData(get(res.data, 'resources', []));
};

const emulatorSensorsDefaultData: EmulatorSensor[] = [];

export const useEmulatorSensors = (patientPrimaryIdentifier?: string) => {
  const { data, ...rest } = useQuery<EmulatorSensor[], Error>({
    queryKey: ['emulator-sensors', patientPrimaryIdentifier],
    queryFn: ({ signal }) => getEmulatorSensors(patientPrimaryIdentifier, signal),
    enabled: !!patientPrimaryIdentifier,
    placeholderData: emulatorSensorsDefaultData,
  });

  return { data: data || emulatorSensorsDefaultData, ...rest };
};
