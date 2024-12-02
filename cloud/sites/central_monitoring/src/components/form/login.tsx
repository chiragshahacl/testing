import PasswordIcon from '@/components/icons/PasswordIcon';
import { PasswordTextField } from '@/styles/StyledComponents';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import InputAdornment from '@mui/material/InputAdornment';
import Typography from '@mui/material/Typography';
import { Formik } from 'formik';
import React, { MutableRefObject, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { FormReference, FormValues } from '@/types/form';

interface LoginFormProps {
  loginHandler: (
    values: FormValues,
    ref: MutableRefObject<FormReference | null>,
    setIsButtonDisabled: (state: boolean) => void
  ) => Promise<void>;
}

const LoginForm = ({ loginHandler }: LoginFormProps) => {
  const { t } = useTranslation();
  const [isButtonDisabled, setIsButtonDisabled] = useState(true);
  const [values, setValues] = useState({ password: '' });
  const [isPasswordFocused, setIsPasswordFocused] = useState(false);
  const formRef = useRef<FormReference | null>(null);

  const schema = Yup.object().shape({
    password: Yup.string().required('Password is required.'),
  });

  const onInputChange = (e: React.ChangeEvent<HTMLTextAreaElement | HTMLInputElement>) => {
    const updatedValues: Record<string, string> = values;
    updatedValues[e.target.name] = e.target.value;
    void schema.isValid(updatedValues).then((valid) => {
      setIsButtonDisabled(!valid);
    });
    setValues((val) => ({ ...val, [e.target.name]: e.target.value }));
  };

  const onSubmit = async () => {
    await loginHandler({ ...values, submit: null }, formRef, setIsButtonDisabled);
  };

  return (
    <Formik<FormValues>
      initialValues={{
        password: '',
        submit: null,
      }}
      innerRef={formRef}
      onSubmit={onSubmit}
    >
      {({ errors, isSubmitting, touched, handleChange, handleSubmit, handleBlur }) => (
        <form noValidate onSubmit={handleSubmit}>
          <Box height={24} />
          <PasswordTextField
            name='password'
            error={!!(touched.password && errors.password)}
            fullWidth
            id='password-input-with-icon-textfield'
            placeholder={isPasswordFocused ? '' : t('LoginPage.passwordPlaceholder')}
            onChange={(e) => {
              handleChange(e);
              onInputChange(e);
            }}
            onFocus={() => setIsPasswordFocused(true)}
            onBlur={(e) => {
              setIsPasswordFocused(false);
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
            <>
              <Box height={24} />
              <Typography variant='error'>{errors.password}</Typography>
            </>
          )}
          {errors.submit && (
            <Box marginTop={24}>
              <Typography variant='error'>
                <>{errors.submit}</>
              </Typography>
            </Box>
          )}
          <Box height={24} />
          <Button
            data-testid='login-button'
            type='submit'
            fullWidth
            variant='contained'
            disabled={errors.submit ? true : isSubmitting || isButtonDisabled}
          >
            {t('LoginPage.logInButton')}
          </Button>
        </form>
      )}
    </Formik>
  );
};

export default LoginForm;
