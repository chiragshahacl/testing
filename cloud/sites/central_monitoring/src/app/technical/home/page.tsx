'use client';

import { useEffect, useState } from 'react';
import EHRintegrationForm from './EHRintegrationForm';
import Grid from '@mui/material/Grid';
import SystemStatusBar from '@/components/layout/SystemStatusBar';
import LowerTopbar from './LowerTopbar';
import IntegratingWithEHR from './IntegratingWithEHR';
import NetworkManager from '@/components/network/NetworkManager';
import { EHRformValues } from '@/types/ehr';
import { useCurrentConfig } from '@/api/useCurrentConfig';
import Loading from '@/app/loading';
import useSearchEhrPatients from '@/api/useSearchEhrPatients';
import { SearchByIdParams } from '@/types/patientSearch';

const TechnicalHome = () => {
  const [processingForm, setProcessingForm] = useState(false);
  const [submitDisabled, setSubmitDisabled] = useState(true);
  const [isIntegrationSuccess, setIsIntegrationSuccess] = useState(false);
  const [isIntegrationComplete, setIsIntegrationComplete] = useState(false);
  const [validPassword, setValidPassword] = useState<string>('');
  const [ehrValues, setEhrValues] = useState<EHRformValues | undefined>(undefined);
  const [ehrPrevValues, setEhrPrevValues] = useState<EHRformValues | undefined>(undefined);

  const currentConfigs = useCurrentConfig();
  const searchParams: SearchByIdParams = { patientPrimaryIdentifier: 'some-id' };
  const { searchPatient } = useSearchEhrPatients(searchParams);

  useEffect(() => {
    if (currentConfigs.isSuccess) {
      setEhrValues(currentConfigs.data);
      setEhrPrevValues(currentConfigs.data);
    }
  }, [currentConfigs.data, currentConfigs.isSuccess]);

  if (currentConfigs.isLoading) {
    return (
      <Grid display='flex' height='90%' justifyContent='center' alignItems='center'>
        <Loading />
      </Grid>
    );
  }

  const onConfigSaved = () => {
    setSubmitDisabled(true);
    setIsIntegrationComplete(true);
  };

  const onConfigSaveFailed = () => {
    setSubmitDisabled(false);
    setIsIntegrationSuccess(false);
    setIsIntegrationComplete(true);
  };

  const onConfigSaveCancelled = () => {
    setSubmitDisabled(false);
    setIsIntegrationComplete(false);
  };

  const onValidateIntegration = async (wasReverted: boolean) => {
    const { isSuccess, isError } = await searchPatient();
    if (isSuccess) {
      if (wasReverted) onConfigSaveCancelled();
      else onConfigSaved();
    } else if (isError) onConfigSaveFailed();
    setProcessingForm(false);
  };

  const content = () => {
    if (processingForm)
      return (
        <IntegratingWithEHR
          values={ehrValues}
          prevValues={ehrPrevValues}
          validPassword={validPassword}
          showIntegrationSuccess={setIsIntegrationSuccess}
          onSave={onConfigSaved}
          onCancelSave={onConfigSaveCancelled}
          validateIntegration={onValidateIntegration}
        />
      );
    else
      return (
        <EHRintegrationForm
          isIntegrationComplete={isIntegrationComplete}
          hideIntegrationStatus={() => setIsIntegrationComplete(false)}
          isIntegrationSuccess={isIntegrationSuccess}
          values={ehrValues}
          setValues={setEhrValues}
          startFormProcessing={() => setProcessingForm(true)}
          submitDisabled={submitDisabled}
          setSubmitDisabled={setSubmitDisabled}
          setValidPassword={setValidPassword}
        />
      );
  };

  return (
    <>
      <SystemStatusBar />
      <>
        <NetworkManager />
        <LowerTopbar />
        <Grid display='flex' height={'calc(100% - 94px)'} flexDirection='column'>
          {content()}
        </Grid>
      </>
    </>
  );
};

export default TechnicalHome;
