import React, { ReactElement, useMemo } from 'react';
import EHRAdmitInfoLine from './components/EHRAdmitInfoLine';
import Typography from '@mui/material/Typography';
import { styled } from '@mui/material/styles';
import AdmissionRejectedModal from '@/components/modals/patientSubmission/AdmissionRejectedModal';
import Box from '@mui/material/Box';
import moment from 'moment';
import { getCachedRuntimeConfig } from '@/utils/runtime';

const StepTitle = styled(Typography)(() => ({
  fontFamily: 'var(--open-sans-font)',
  fontSize: '24px',
  fontWeight: 500,
  lineHeight: '27.58px',
  textAlign: 'center',
  width: '100%',
  marginBottom: '10px',
}));

const SubmissionInfoLine = styled(Typography)(() => ({
  fontSize: '16px',
  fontWeight: 400,
  lineHeight: '21.79px',
  textAlign: 'center',
}));

interface EHRConfirmAdmitRequestProps {
  values: Record<string, string>;
  dateSubmissionSent: string;
  wasRejected: boolean;
  onRejected: () => Promise<void>;
}

const mapFieldToTitle: Record<string, string> = {
  patientPrimaryIdentifier: 'Patient ID',
  patientFirstName: 'First Name',
  patientLastName: 'Last Name',
  patientDob: 'DOB',
  patientGender: 'Sex',
};

const HOSPITAL_TIMEZONE = getCachedRuntimeConfig().HOSPITAL_TZ ?? 'UTC';

const EHRRequestSubmitted = ({
  values,
  dateSubmissionSent,
  wasRejected,
  onRejected,
}: EHRConfirmAdmitRequestProps) => {
  const renderValueLines = useMemo(() => {
    const result: ReactElement[] = [];
    Object.entries(mapFieldToTitle).forEach(([key, value]) => {
      result.push(<EHRAdmitInfoLine key={key} fieldName={value} value={values[key]} />);
    });
    return result;
  }, [values]);

  return (
    <>
      <AdmissionRejectedModal isOpen={wasRejected} onConfirm={onRejected} />
      <Box mb='30px'>
        <StepTitle>Confirm Patient Information</StepTitle>
        <SubmissionInfoLine>
          Admission Request Sent:{' '}
          {moment.tz(dateSubmissionSent, 'UTC').tz(HOSPITAL_TIMEZONE).format('yyyy-MM-DD HH:mm')}
        </SubmissionInfoLine>
        <SubmissionInfoLine>
          Patient information need to be confirmed through patient monitor.{' '}
        </SubmissionInfoLine>
      </Box>
      {renderValueLines}
    </>
  );
};

export default EHRRequestSubmitted;
