import { EmulatorUpdatedSensorModes } from '@/types/emulator';
import { emulatorClient } from '@/utils/httpClient';

import { useMutation } from '@tanstack/react-query';

interface UpdateEmulatorsModesParams {
  sensors: EmulatorUpdatedSensorModes[];
}

const updateEmulatorsModes = async ({ sensors }: UpdateEmulatorsModesParams) =>
  await emulatorClient.put('/emulator/sensor/mode/batch', {
    sensors,
  });

export const useUpdateEmulatorsModes = () => {
  return useMutation({
    mutationKey: ['update-emulators-modes'],
    mutationFn: (params: UpdateEmulatorsModesParams) => updateEmulatorsModes(params),
  });
};
