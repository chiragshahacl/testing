import React from 'react';
import EHRQuickAdmitForm from './components/EHRQuickAdmitForm';

export type EHRQuickAdmitFormValues = {
  firstName: string;
  lastName: string;
  dob?: string;
  sex?: string;
  submit?: boolean | null;
};

export type EHRQuickAdmitFormInitialData = {
  patientPrimaryIdentifier?: string;
  firstName?: string;
  lastName?: string;
  dob?: string;
  sex?: string;
};

interface LoginFormProps {
  initialData?: EHRQuickAdmitFormInitialData;
  searchHandler: (values: EHRQuickAdmitFormValues) => void;
  onBack: () => void;
}

const EHRQuickAdmitFormController = ({ initialData, searchHandler, onBack }: LoginFormProps) => {
  return (
    <>
      <EHRQuickAdmitForm initialData={initialData} searchHandler={searchHandler} onBack={onBack} />
    </>
  );
};

export default EHRQuickAdmitFormController;
