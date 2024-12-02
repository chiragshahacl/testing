'use client';

import { Dispatch, SetStateAction, useEffect, useState } from 'react';
import { useIntegrateWithEHR } from '@/api/useIntegrateWithEHR';
import Loading from '@/app/loading';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import { openSansFont } from '@/utils/fonts';
import { EHRformValues } from '@/types/ehr';

interface IntegratingWithEHRProps {
  values?: EHRformValues;
  prevValues?: EHRformValues;
  showIntegrationSuccess: Dispatch<SetStateAction<boolean>>;
  onSave: () => void;
  onCancelSave: () => void;
  validateIntegration: (wasReverted: boolean) => Promise<void>;
  validPassword: string;
}

const IntegratingWithEHR = ({
  values,
  prevValues,
  showIntegrationSuccess,
  validateIntegration,
  validPassword,
}: IntegratingWithEHRProps) => {
  const [cancelling, setCancelling] = useState(false);

  const { integrateEHR } = useIntegrateWithEHR();

  const saveConfig = async (config: EHRformValues, isRevert = false) => {
    await integrateEHR(
      {
        password: validPassword,
        config: {
          MLLP_HOST: config.host,
          MLLP_PORT: config.port,
          MLLP_EXPORT_INTERVAL_MINUTES: config.interval,
        },
      },
      {
        onSuccess: () => showIntegrationSuccess(true),
        onError: () => showIntegrationSuccess(false),
        onSettled: () => {
          setTimeout(() => {
            void validateIntegration(isRevert);
          }, 10000);
        },
      }
    );
  };

  const handleRevertConfig = async () => {
    setCancelling(true);
    if (prevValues) await saveConfig(prevValues, true);
  };

  useEffect(() => {
    if (values?.host && values?.port && values?.interval) {
      void saveConfig(values);
    }
  }, []);

  return (
    <Grid justifyContent='center' margin='auto'>
      <Loading height={114.25} size={114.25} />
      <Box height={24} />
      <Typography variant='h1'>Integrating with EHR...</Typography>
      <Box height={8} />
      <Typography variant='subtitle1' textAlign='center' fontFamily={openSansFont.style.fontFamily}>
        This may take a few minutes
      </Typography>
      <Box height={80} />
      <Grid display='flex' justifyContent='center'>
        <Button
          sx={{ width: 273 }}
          variant='contained'
          color='primary'
          data-testid='cancel-button'
          disabled={cancelling}
          onClick={() => void handleRevertConfig()}
        >
          Cancel
        </Button>
      </Grid>
    </Grid>
  );
};

export default IntegratingWithEHR;
