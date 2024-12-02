import CloseIcon from '@/components/icons/CloseIcon';
import PasswordIcon from '@/components/icons/PasswordIcon';
import { PasswordTextField, StyledModalContainer } from '@/styles/StyledComponents';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import InputAdornment from '@mui/material/InputAdornment';
import Modal from '@mui/material/Modal';
import Typography from '@mui/material/Typography';
import { Formik, FormikHelpers, FormikProps } from 'formik';
import React, { ReactNode, useEffect, useRef, useState } from 'react';
import * as Yup from 'yup';

export type FormValues = {
  password: string;
  submit: null;
};

type Reference = FormikProps<FormValues>;

interface PasswordValidationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (
    values: FormValues,
    { setErrors, setSubmitting }: FormikHelpers<FormValues>
  ) => Promise<void>;
  onBack?: () => void;
  description?: ReactNode;
}

const PasswordValidationModal = ({
  isOpen,
  onClose,
  onSubmit,
  onBack,
  description = (
    <Typography my={24} variant='subtitle1'>
      Please enter the current password.
    </Typography>
  ),
}: PasswordValidationModalProps) => {
  const ref = useRef<Reference | null>(null);

  const [isButtonDisabled, setIsButtonDisabled] = useState<boolean>(true);

  const schema = Yup.object().shape({
    password: Yup.string().required('Password is required.'),
  });

  const onInputChange = (e: React.ChangeEvent<HTMLTextAreaElement | HTMLInputElement>) => {
    void schema.isValid({ password: e.target.value }).then((valid) => {
      setIsButtonDisabled(!valid);
    });
  };

  useEffect(() => {
    // Disables confirm button when modal is closed
    if (!isOpen) {
      setIsButtonDisabled(true);
    }
  }, [isOpen]);

  return (
    <Modal open={isOpen} sx={{ display: 'flex', flex: 1 }}>
      <StyledModalContainer container item lg={5}>
        <Grid
          item
          display='flex'
          flexDirection='row'
          justifyContent='space-between'
          alignItems='center'
          sx={{ width: '100%' }}
        >
          <Typography variant='h1'>Password required</Typography>
          <CloseIcon handleClick={onClose} />
        </Grid>
        {description}
        <Formik<FormValues>
          initialValues={{
            password: '',
            submit: null,
          }}
          innerRef={ref}
          onSubmit={onSubmit}
        >
          {({ values, errors, isSubmitting, touched, handleChange, handleSubmit, handleBlur }) => (
            <form
              noValidate
              onSubmit={handleSubmit}
              style={{ width: '100%', gap: '24px', display: 'grid' }}
            >
              <PasswordTextField
                name='password'
                error={!!(touched.password && errors.password)}
                fullWidth
                id='password-input-with-icon-textfield'
                placeholder='Password'
                onChange={(e) => {
                  handleChange(e);
                  onInputChange(e);
                }}
                onBlur={(e) => {
                  handleBlur(e);
                  onInputChange(e);
                }}
                type='password'
                InputProps={{
                  startAdornment: (
                    <InputAdornment position='start'>
                      <PasswordIcon invalid={!!(touched.password && errors.password)} />
                    </InputAdornment>
                  ),
                }}
                value={values.password}
                variant='outlined'
              />
              {errors.password && touched.password && (
                <Typography variant='error'>
                  <>{errors.password}</>
                </Typography>
              )}
              {errors.submit && (
                <Typography variant='error'>
                  <>{errors.submit}</>
                </Typography>
              )}
              <Button
                type='submit'
                data-testid='submit-button'
                variant='contained'
                fullWidth
                disabled={!!(errors.submit || errors.password) || isSubmitting || isButtonDisabled}
              >
                Confirm
              </Button>
              {onBack && (
                <Button
                  data-testid='back-to-edit-button'
                  variant='outlined'
                  fullWidth
                  onClick={onBack}
                >
                  Back to edit
                </Button>
              )}
            </form>
          )}
        </Formik>
      </StyledModalContainer>
    </Modal>
  );
};

export default PasswordValidationModal;
