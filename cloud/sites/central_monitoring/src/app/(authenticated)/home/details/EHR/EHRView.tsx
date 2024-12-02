import { useEffect, useMemo, useState } from 'react';
import EHRAdmitSelection from './EHRAdmitSelection';
import { EHRStep } from '@/utils/ehr';
import EHRSearchFormController from './EHRSearchFormController';
import { noop } from 'lodash';
import Box from '@mui/material/Box';
import { styled } from '@mui/material';
import EHRQuickAdmitFormController, {
  EHRQuickAdmitFormValues,
} from './EHRQuickAdmitFormController';
import EHRConfirmAdmitRequest from './EHRConfirmAdmitRequest';
import useSearchEhrPatients from '@/api/useSearchEhrPatients';
import { EHRPatientType } from '@/types/patient';
import EHRSearchResults from './EHRSearchResults';
import EHRRequestSubmitted from './EHRRequestSubmitted';
import { useQueryClient } from '@tanstack/react-query';
import { SearchByIdParams, SearchByNameParams } from '@/types/patientSearch';
import { BedType } from '@/types/bed';
import { EncounterStatus } from '@/types/encounters';
import { acknowledgePatientAdmissionRejection } from '@/api/patientsApi';
import { useEHRAdmit } from '@/api/useEhrAdmit';
import { useQuickAdmit } from '@/api/useQuickAdmit';
import Loading from '@/app/loading';

enum RequestType {
  QUICK_ADMIT = 'QUICK_ADMIT',
  SEARCH = 'SEARCH',
}

type ConfirmRequestData = {
  flow: RequestType;
  values: {
    patientPrimaryIdentifier?: string;
    firstName?: string;
    lastName?: string;
    dob?: string;
    sex?: string;
  };
};

const ComponentContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: theme.palette.primary.dark,
  flex: 1,
  width: '100%',
  borderRadius: '8px',
  gap: '10px',
  padding: '20px 25px',
}));

interface EHRViewProps {
  selectedBed: BedType;
  currentStep: EHRStep;
  setCurrentStep: (newStep: EHRStep) => void;
}

const ERROR_MESSAGES = {
  NO_PATIENT: 'No results found',
  ALREADY_ADMITTED: 'Patient has already been admitted to the ANNE One system',
  ADMISSION_REQUEST_ERROR: 'There was an error sending the admission request. Please retry',
  CONFIRM_REJECTION_ERROR: 'There was an error confirming the rejection. Please retry',
};

const EHRView = ({ selectedBed, currentStep, setCurrentStep }: EHRViewProps) => {
  const [confirmRequestData, setConfirmRequestData] = useState<ConfirmRequestData | null>(null);
  const [searchParams, setSearchParams] = useState<SearchByIdParams | SearchByNameParams | null>(
    null
  );
  const [errorMessage, setErrorMessage] = useState<string>('');

  const {
    foundPatients,
    searchPatient,
    isFetching,
    isFetched,
    searchPatientStatus,
    searchPatientErrorType,
    searchPatientLoading,
  } = useSearchEhrPatients(searchParams);
  const { ehrAdmit, ehrAdmitLoading } = useEHRAdmit();
  const { quickAdmit, quickAdmitLoading } = useQuickAdmit();
  const queryClient = useQueryClient();

  const onSendAssignRequest = async () => {
    setErrorMessage('');
    if (confirmRequestData) {
      if (confirmRequestData.flow === RequestType.SEARCH) {
        if (confirmRequestData.values.patientPrimaryIdentifier) await onAssignSearchedPatient();
        else noop(); // @debt: HANDLE NO ID WHEN SUBMITTING (SHOULD NEVER HAPPEN)
      } else if (confirmRequestData.flow === RequestType.QUICK_ADMIT)
        if (confirmRequestData.values.firstName && confirmRequestData.values.lastName) {
          await onQuickAdmitPatient();
        } else noop();
      // @debt: HANDLE NO FIRST & LAST NAMES WHEN SUBMITTING (SHOULD NEVER HAPPEN)
    }
  };

  const onSearchPatient = async (values: {
    patientPrimaryIdentifier?: string;
    firstName?: string;
    lastName?: string;
    dob?: string;
  }): Promise<boolean> => {
    setErrorMessage('');
    let success = false;
    if (values.patientPrimaryIdentifier) {
      setSearchParams({
        patientPrimaryIdentifier: values.patientPrimaryIdentifier,
      });
    } else if (values.firstName && values.lastName) {
      setSearchParams({
        firstName: values.firstName,
        lastName: values.lastName,
        dob: values?.dob,
      });
    }
    try {
      await searchPatient();
      success = true;
    } catch (error) {
      success = false;
    }
    return success;
  };

  const onAssignSearchedPatient = async () => {
    setErrorMessage('');
    if (confirmRequestData && confirmRequestData.values.patientPrimaryIdentifier) {
      await ehrAdmit(
        {
          ...confirmRequestData.values,
          patientPrimaryIdentifier: confirmRequestData.values.patientPrimaryIdentifier || '',
          bedId: selectedBed.id,
        },
        {
          onSuccess: () => {
            void queryClient.invalidateQueries(['bed']);
          },
          onError: () => {
            setErrorMessage(ERROR_MESSAGES.ADMISSION_REQUEST_ERROR);
          },
        }
      );
    }
    // @debt: HANDLE NO CONFIRM REQUEST DATA (SHOULD NEVER HAPPEN SINCE IT'S CONTROLLED BEFORE CALLING)
  };

  const onQuickAdmitPatient = async () => {
    if (confirmRequestData?.values.firstName && confirmRequestData?.values.lastName) {
      await quickAdmit(
        {
          ...confirmRequestData.values,
          firstName: confirmRequestData.values.firstName || '',
          lastName: confirmRequestData.values.lastName || '',
          bedId: selectedBed.id,
        },
        {
          onSuccess: () => {
            void queryClient.invalidateQueries(['bed']);
          },
          onError: () => {
            setErrorMessage(ERROR_MESSAGES.ADMISSION_REQUEST_ERROR);
          },
        }
      );
    }
    // @debt: HANDLE NO CONFIRM REQUEST DATA (SHOULD NEVER HAPPEN SINCE IT'S CONTROLLED BEFORE CALLING)
  };

  const onConfirmRejection = async () => {
    setCurrentStep(EHRStep.UNASSIGNED);

    try {
      if (selectedBed.patient?.patientId) {
        await acknowledgePatientAdmissionRejection(selectedBed.patient?.patientId);
        void queryClient.invalidateQueries(['bed']);
      }
    } catch (error) {
      setErrorMessage(ERROR_MESSAGES.CONFIRM_REJECTION_ERROR);
    }
  };

  const encounterStatus = useMemo(() => {
    return selectedBed.encounter?.status;
  }, [selectedBed]);

  useEffect(() => {
    switch (encounterStatus) {
      case EncounterStatus.CANCELLED:
      case EncounterStatus.PLANNED:
        setCurrentStep(EHRStep.SUBMITTED);
        break;
      default:
        setCurrentStep(EHRStep.UNASSIGNED);
        break;
    }
  }, [encounterStatus]);

  useEffect(() => {
    if (!isFetching) {
      if (isFetched) {
        if (
          searchPatientStatus !== 422 &&
          searchPatientErrorType !== 'value_error.patient_already_monitored'
        ) {
          if (foundPatients && foundPatients.length > 0) {
            if (foundPatients.length > 1) {
              setConfirmRequestData(null);
              setCurrentStep(EHRStep.SEARCH_RESULTS);
            } else {
              setConfirmRequestData({ values: { ...foundPatients[0] }, flow: RequestType.SEARCH });
              setCurrentStep(EHRStep.CONFIRM_REQUEST);
            }
          } else {
            setErrorMessage(ERROR_MESSAGES.NO_PATIENT);
          }
        } else {
          setErrorMessage(ERROR_MESSAGES.ALREADY_ADMITTED);
        }
      }
    }
  }, [foundPatients, isFetching, isFetched, searchPatientStatus, searchPatientErrorType]);

  const getStepView = () => {
    if (currentStep === EHRStep.SEARCH) {
      return (
        <EHRSearchFormController
          searchHandler={onSearchPatient}
          onBack={() => {
            setErrorMessage('');
            setCurrentStep(EHRStep.UNASSIGNED);
          }}
          errorMessage={errorMessage}
          dismissNoPatientError={() => setErrorMessage('')}
        />
      );
    } else if (currentStep === EHRStep.SEARCH_RESULTS) {
      return (
        <EHRSearchResults
          foundPatients={foundPatients || []}
          submitHandler={(selectedPatient: EHRPatientType) => {
            setConfirmRequestData({ values: selectedPatient, flow: RequestType.SEARCH });
            setCurrentStep(EHRStep.CONFIRM_REQUEST);
          }}
          onBack={() => {
            void queryClient.resetQueries(['search-patient'], { exact: true });
            setCurrentStep(EHRStep.SEARCH);
          }}
        />
      );
    } else if (currentStep === EHRStep.QUICK_ADMIT) {
      return (
        <EHRQuickAdmitFormController
          initialData={confirmRequestData?.values}
          searchHandler={(values: EHRQuickAdmitFormValues) => {
            setConfirmRequestData({ values, flow: RequestType.QUICK_ADMIT });
            setCurrentStep(EHRStep.CONFIRM_REQUEST);
          }}
          onBack={() => {
            setConfirmRequestData(null);
            setCurrentStep(EHRStep.UNASSIGNED);
          }}
        />
      );
    } else if (currentStep === EHRStep.CONFIRM_REQUEST) {
      return (
        <EHRConfirmAdmitRequest
          onSubmit={onSendAssignRequest}
          values={confirmRequestData?.values || {}}
          onBack={() => {
            setErrorMessage('');
            if (confirmRequestData?.flow === RequestType.QUICK_ADMIT)
              setCurrentStep(EHRStep.QUICK_ADMIT);
            else setCurrentStep(EHRStep.SEARCH);
          }}
          errorMessage={errorMessage}
        />
      );
    } else if (currentStep === EHRStep.SUBMITTED) {
      return (
        <EHRRequestSubmitted
          values={selectedBed.patient || {}}
          dateSubmissionSent={selectedBed.encounter?.createdAt || ''}
          wasRejected={selectedBed.encounter?.status === EncounterStatus.CANCELLED}
          onRejected={onConfirmRejection}
        />
      );
    }

    return <EHRAdmitSelection updateEHRState={setCurrentStep} />;
  };

  if (searchPatientLoading || ehrAdmitLoading || quickAdmitLoading) {
    return (
      <ComponentContainer>
        <Loading />
      </ComponentContainer>
    );
  }

  return <ComponentContainer>{getStepView()}</ComponentContainer>;
};

export default EHRView;
