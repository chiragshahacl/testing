'use client';

import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

import { useEmulatorSensors } from '@/api/useEmulatorSensors';
import { usePatients } from '@/api/usePatients';
import { useUpdateEmulatorsModes } from '@/api/useUpdateEmulatorSensor';
import useSession from '@/hooks/useSession';
import { EmulatorUpdateEmulatorModes, EmulatorUpdatedSensorModes } from '@/types/emulator';
import { PatientType } from '@/types/patient';
import Loading from '../loading';
import EmulatorsModal from './EmulatorsModal';

/**
 * Screen only for internal usage. Not intended for final user. Handles flows
 * with the emulator to simulate different cases. Has no use in production
 * environments since there is no emulator there
 */
const EmulatorUpdates = () => {
  const router = useRouter();
  const { accessToken, refreshToken, authenticating } = useSession();
  const [isModalOpen, setModalOpen] = useState<boolean>(true);
  const [selectedPatient, setSelectedPatient] = useState<PatientType | null>(null);

  const updateEmulatorMode = useUpdateEmulatorsModes();

  const patients = usePatients();
  const sensors = useEmulatorSensors(selectedPatient?.primaryIdentifier);

  const handleClickPatient = (patient: PatientType) => {
    void sensors.refetch();
    setSelectedPatient(patient);
    setModalOpen(true);
  };

  const onSave = (newModes: Record<string, Record<string, string>>) => {
    const updatedSensors: EmulatorUpdatedSensorModes[] = [];
    Object.entries(newModes).forEach((sensorEmulators) => {
      const sensorId = sensorEmulators[0];
      const emulatorsModes = sensorEmulators[1];
      const updatedEmulatorModes: EmulatorUpdateEmulatorModes[] = [];
      if (sensorId) {
        Object.entries(emulatorsModes).forEach((newEmulatorModes) => {
          const name = newEmulatorModes[0];
          const mode = newEmulatorModes[1];
          updatedEmulatorModes.push({
            name,
            mode,
          });
        });
        if (updatedEmulatorModes.length > 0) {
          updatedSensors.push({
            id: sensorId,
            emulators: updatedEmulatorModes,
          });
        }
      }
    });
    if (updatedSensors.length > 0) {
      updateEmulatorMode.mutate(
        { sensors: updatedSensors },
        {
          onSuccess: () => {
            setModalOpen(false);
          },
        }
      );
    }
  };

  useEffect(() => {
    // Redirects user to login if not authorized
    if (!authenticating && !(accessToken && refreshToken)) {
      router.replace('/');
    }
  }, [accessToken, authenticating, refreshToken, router]);

  if (patients.isFetching) {
    return (
      <Box display='flex' width='100%' height='100%' alignContent='center' flexWrap='wrap'>
        <Loading height={64} />
      </Box>
    );
  }

  return (
    <>
      <EmulatorsModal
        isLoading={updateEmulatorMode.isLoading || sensors.isFetching}
        isOpen={isModalOpen}
        onSave={onSave}
        onClose={() => {
          setModalOpen(false);
        }}
        patient={selectedPatient}
        sensors={sensors.data}
      />
      <Typography mt='20px' width='100%' fontSize='42px' textAlign='center'>
        Patients
      </Typography>
      <Box display='flex' mt='20px' flexWrap='wrap'>
        {patients.data &&
          patients.data.map((patient) => (
            <Box
              key={`patient_${patient.id}`}
              width='50%'
              onClick={() => {
                handleClickPatient(patient);
              }}
            >
              <Typography>
                {patient.givenName} {patient.familyName}
              </Typography>
            </Box>
          ))}
      </Box>
    </>
  );
};

export default EmulatorUpdates;
