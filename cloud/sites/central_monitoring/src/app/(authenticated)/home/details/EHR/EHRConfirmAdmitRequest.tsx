import React, { ReactElement, useMemo, useState } from 'react';
import EHRAdmitInfoLine from './components/EHRAdmitInfoLine';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import { styled } from '@mui/material/styles';
import AgeWarningModal from '@/components/modals/patientSubmission/AgeWarningModal';
import { checkAgeLessThanYears } from '@/utils/ageCheck';

const StepTitle = styled(Typography)(() => ({
  fontFamily: 'var(--open-sans-font)',
  fontSize: '24px',
  fontWeight: 500,
  lineHeight: '27.58px',
  textAlign: 'center',
  width: '100%',
  marginBottom: '30px',
}));

interface EHRConfirmAdmitRequestProps {
  onSubmit: () => Promise<void>;
  values: Record<string, string>;
  onBack: () => void;
  errorMessage: string;
}

const mapFieldToTitle: Record<string, string> = {
  patientPrimaryIdentifier: 'Patient ID',
  firstName: 'First Name',
  lastName: 'Last Name',
  dob: 'DOB',
  sex: 'Sex',
};

const EHRConfirmAdmitRequest = ({
  onSubmit,
  values,
  onBack,
  errorMessage,
}: EHRConfirmAdmitRequestProps) => {
  const [showAgeWarning, setShowAgeWarning] = useState(false);

  const renderValueLines = useMemo(() => {
    const result: ReactElement[] = [];
    Object.entries(mapFieldToTitle).forEach(([key, value]) => {
      result.push(<EHRAdmitInfoLine key={key} fieldName={value} value={values[key]} />);
    });
    return result;
  }, [values]);

  const checkAge = () => {
    if (values['dob'] && checkAgeLessThanYears(values['dob'], 12)) setShowAgeWarning(true);
    else {
      setShowAgeWarning(false);
      void onSubmit();
    }
  };

  return (
    <>
      <AgeWarningModal
        isOpen={showAgeWarning}
        onConfirm={async () => {
          setShowAgeWarning(false);
          await onSubmit();
        }}
        onCancel={() => {
          setShowAgeWarning(false);
        }}
      />
      <StepTitle>PATIENT ADMISSION REQUEST</StepTitle>
      {renderValueLines}
      {errorMessage && (
        <Box marginTop={24} textAlign='center' width='70%'>
          <Typography variant='error'>{errorMessage}</Typography>
        </Box>
      )}
      <Box display='flex' flexDirection='row' gap='24px' width='100%' mt='52px'>
        <Button
          data-testid='back-button'
          type='reset'
          variant='outlined'
          sx={{ height: '48px', flex: 1 }}
          onClick={onBack}
        >
          Back
        </Button>
        <Button
          data-testid='search-button'
          type='submit'
          variant='contained'
          sx={{ height: '48px', flex: 1 }}
          onClick={() => checkAge()}
        >
          Send admission request to Patient Monitor
        </Button>
      </Box>
    </>
  );
};

export default EHRConfirmAdmitRequest;
