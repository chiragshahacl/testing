import {
  ErrorText,
  LabelContainer,
  LabelHelper,
  LabelText,
  StyledTextField,
} from '@/styles/StyledComponents';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import { FormikHelpers, useFormik } from 'formik';
import React, { Dispatch, SetStateAction, useEffect, useState } from 'react';
import Grid from '@mui/material/Grid';
import { openSansFont } from '@/utils/fonts';
import theme from '@/theme/theme';
import EHRconfirmationModal from '@/components/modals/technical/EHRconfirmation';
import { get } from 'lodash';
import PasswordValidationModal, { FormValues } from '@/components/modals/PasswordValidationModal';
import { useTechnicalPasswordValidation } from '@/api/usePasswordValidation';
import { ServerErrorResponse } from '@/types/response';
import { getAuthErrorMessage } from '@/api/authErrors';
import IntegrationStatus from '@/components/modals/technical/IntegrationStatus';
import { ehrFormSchema } from '@/schemas/ehrFormSchema';
import { EHRformValues } from '@/types/ehr';

interface EHRintegrationFormProps {
  values?: EHRformValues;
  setValues: Dispatch<SetStateAction<EHRformValues | undefined>>;
  startFormProcessing: () => void;
  isIntegrationSuccess: boolean;
  isIntegrationComplete: boolean;
  hideIntegrationStatus: () => void;
  submitDisabled: boolean;
  setSubmitDisabled: Dispatch<SetStateAction<boolean>>;
  setValidPassword: Dispatch<SetStateAction<string>>;
}

const EHRintegrationForm = ({
  values,
  setValues,
  startFormProcessing,
  isIntegrationSuccess,
  isIntegrationComplete,
  hideIntegrationStatus,
  submitDisabled,
  setSubmitDisabled,
  setValidPassword,
}: EHRintegrationFormProps) => {
  const [isValidatePasswordOpen, setIsValidatePasswordOpen] = useState(false);
  const [shouldValidate, setShouldValidate] = useState(false);
  const [showConfirmationModal, setShowConfirmationModal] = useState(false);
  const { validate } = useTechnicalPasswordValidation();

  const formik = useFormik({
    initialValues: {
      host: values?.host,
      port: values?.port,
      interval: values?.interval,
    },
    validationSchema: ehrFormSchema,
    onSubmit: (values) => {
      setValues(values as unknown as EHRformValues);
      setShowConfirmationModal(true);
    },
    validateOnChange: shouldValidate,
    validateOnBlur: false,
  });

  const onValidateSubmit = async (
    values: FormValues,
    { setErrors, setSubmitting }: FormikHelpers<FormValues>
  ) => {
    const { password } = values;
    await validate(
      { password },
      {
        onSuccess: () => {
          setValidPassword(password);
          setIsValidatePasswordOpen(false);
          startFormProcessing();
        },
        onError: (err: ServerErrorResponse) => {
          setErrors({ password: getAuthErrorMessage(err) });
        },
        onSettled: () => {
          setSubmitting(false);
        },
      }
    );
  };

  useEffect(() => {
    const updateValues = async () => {
      await formik.setValues({
        host: values?.host,
        port: values?.port,
        interval: values?.interval,
      });
    };

    void updateValues();
  }, [values]);

  return (
    <>
      <PasswordValidationModal
        isOpen={isValidatePasswordOpen}
        onClose={() => setIsValidatePasswordOpen(false)}
        onSubmit={onValidateSubmit}
        onBack={() => {
          setSubmitDisabled(false);
          setIsValidatePasswordOpen(false);
        }}
        description={
          <Typography
            fontFamily={openSansFont.style.fontFamily}
            variant='subtitle1'
            margin={(theme) => theme.spacing(8, 0, 48, 0)}
          >
            Please enter the password to save the settings.
          </Typography>
        }
      />
      <IntegrationStatus
        open={isIntegrationComplete}
        successStatus={isIntegrationSuccess}
        handleClose={() => {
          if (isIntegrationSuccess) hideIntegrationStatus();
          else {
            setSubmitDisabled(false);
            hideIntegrationStatus();
          }
        }}
      />
      <EHRconfirmationModal
        isOpen={showConfirmationModal}
        host={get(values, 'host', '')}
        port={get(values, 'port', 0)}
        interval={get(values, 'interval', 0)}
        onBackToEdit={() => {
          setShowConfirmationModal(false);
          setSubmitDisabled(false);
        }}
        onConfirm={() => {
          setShowConfirmationModal(false);
          setIsValidatePasswordOpen(true);
        }}
      />
      <Grid
        flex={1}
        width='100vw'
        display='flex'
        flexDirection='column'
        justifyContent='center'
        alignSelf='center'
        gap={72}
        paddingX={244}
      >
        <Box>
          <Typography variant='h1'>EHR Integration</Typography>
          <Box height={8} />
          <Typography fontFamily={openSansFont.style.fontFamily} variant='subtitle1'>
            Configure and integrate with EHR platform.
          </Typography>
        </Box>
        <form>
          <LabelContainer htmlFor='host'>
            <LabelText>Host Address </LabelText>
            <LabelHelper>(Required)</LabelHelper>
          </LabelContainer>
          <StyledTextField
            fullWidth
            {...formik.getFieldProps('host')}
            id='host'
            name='host'
            error={!!(formik.touched.host && formik.errors.host)}
            onChange={(e) => {
              setSubmitDisabled(
                !(
                  e.currentTarget.value.trim() !== '' &&
                  formik.values.port &&
                  formik.values.interval
                )
              );
              formik.handleChange(e);
            }}
            data-testid='host'
          />
          {formik.touched.host && formik.errors.host ? (
            <ErrorText variant='error'>{formik.errors.host}</ErrorText>
          ) : null}
          <Box height={24} />

          <LabelContainer htmlFor='port'>
            <LabelText>Server Port </LabelText>
            <LabelHelper>(Required)</LabelHelper>
          </LabelContainer>
          <StyledTextField
            fullWidth
            {...formik.getFieldProps('port')}
            id='port'
            name='port'
            error={!!(formik.touched.host && formik.errors.port)}
            onChange={(e) => {
              setSubmitDisabled(
                !(
                  e.currentTarget.value.trim() !== '' &&
                  formik.values.host &&
                  formik.values.host.trim() !== '' &&
                  formik.values.interval
                )
              );
              formik.handleChange(e);
            }}
            data-testid='port'
          />
          {formik.touched.port && formik.errors.port ? (
            <ErrorText variant='error'>{formik.errors.port}</ErrorText>
          ) : null}
          <Box height={24} />

          <LabelContainer htmlFor='interval'>
            <LabelText>Transmission Interval (Minutes) </LabelText>
            <LabelHelper>(Required)</LabelHelper>
          </LabelContainer>
          <StyledTextField
            fullWidth
            {...formik.getFieldProps('interval')}
            id='interval'
            name='interval'
            error={!!(formik.touched.host && formik.errors.interval)}
            onChange={(e) => {
              setSubmitDisabled(
                !(
                  e.currentTarget.value.trim() !== '' &&
                  formik.values.host &&
                  formik.values.host.trim() !== '' &&
                  formik.values.port
                )
              );
              formik.handleChange(e);
            }}
            data-testid='interval'
          />
          {formik.touched.interval && formik.errors.interval ? (
            <ErrorText variant='error'>{formik.errors.interval}</ErrorText>
          ) : (
            <ErrorText color={theme.palette.grey[600]} variant='error'>
              Enter a value between 1 - 100
            </ErrorText>
          )}
          <Box height={24} />

          <Button
            fullWidth
            variant='contained'
            color='primary'
            disabled={submitDisabled}
            onClick={() => {
              setShouldValidate(true);
              setSubmitDisabled(true);
              formik.handleSubmit();
            }}
            data-testid='save-button'
          >
            Save
          </Button>
        </form>
      </Grid>
    </>
  );
};

export default EHRintegrationForm;
