import { PatientsData } from '@/context/PatientsContext';
import { useContext } from 'react';

/**
 * @description Hook for accesing content from the PatientsData Context safely
 * @returns Context for PatientsData
 */
const usePatientData = () => {
  const context = useContext(PatientsData);

  if (context === null) {
    throw new Error('usePatientData must be used within a PatientsProvider');
  }

  return context;
};

export default usePatientData;
