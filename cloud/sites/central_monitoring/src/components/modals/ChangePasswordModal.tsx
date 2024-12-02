import { getAuthErrorMessage } from '@/api/authErrors';
import { useChangePassword } from '@/api/useChangePassword';
import CloseIcon from '@/components/icons/CloseIcon';
import PasswordIcon from '@/components/icons/PasswordIcon';
import { PasswordTextField, StyledModalContainer } from '@/styles/StyledComponents';
import { ServerErrorResponse } from '@/types/response';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import InputAdornment from '@mui/material/InputAdornment';
import Modal from '@mui/material/Modal';
import Tooltip, { TooltipProps, tooltipClasses } from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import { styled } from '@mui/material/styles';
import { Formik, FormikHelpers, FormikProps, FormikValues } from 'formik';
import { useEffect, useRef, useState } from 'react';
import * as Yup from 'yup';
import ChecklistItem from '../ChecklistItem';

const PasswordTooltip = styled(({ className, ...props }: TooltipProps) => (
  <Tooltip {...props} classes={{ popper: className }} />
))(({ theme }) => ({
  [`& .${tooltipClasses.tooltip}`]: {
    backgroundColor: theme.palette.common.black,
    color: theme.palette.common.white,
    fontSize: theme.typography.pxToRem(12),
  },
  [`& .${tooltipClasses.arrow}`]: {
    color: theme.palette.common.black,
    transform: 'translate(140px, 0px) !important',
  },
}));

const CONDITION_KEYS = {
  LENGTH: 'length',
  UPPERCASE: 'uppercase',
  LOWERCASE: 'lowercase',
  NUMBER: 'number',
  SPECIAL: 'special',
};

const DEFAULT_CONDITIONS = {
  [CONDITION_KEYS.LENGTH]: false,
};

interface ChangePasswordModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  currentPassword: string;
}

type FormValues = {
  newPassword: string;
  reEnteredPassword: string;
  submit: null;
};

type Reference = FormikProps<FormValues>;

const ChangePasswordModal = ({
  isOpen,
  onClose,
  currentPassword,
  onSuccess,
}: ChangePasswordModalProps) => {
  const [isButtonDisabled, setIsButtonDisabled] = useState<boolean>(true);
  const [conditionsMet, setConditionsMet] = useState<Record<string, boolean>>(DEFAULT_CONDITIONS);
  const ref = useRef<Reference | null>(null);
  const { changePassword } = useChangePassword();

  const schema = Yup.object().shape({
    newPassword: Yup.string()
      .matches(/^.{4,}$/, 'Password does not meet criteria.')
      .required('Password is required.'),
    reEnteredPassword: Yup.string()
      .oneOf([Yup.ref('newPassword'), undefined], 'Password does not match previous entry.')
      .required('This field is required'),
  });

  const checkPasswordPolicies = (password: string) => {
    const lengthCheck = password.length >= 4;

    setConditionsMet({
      [CONDITION_KEYS.LENGTH]: lengthCheck,
    });
  };

  const onInputChange = (
    e: React.ChangeEvent<HTMLTextAreaElement | HTMLInputElement>,
    values: FormikValues
  ) => {
    const newValues = values;
    newValues[e.target.name] = e.target.value;
    if (e.target.name === 'newPassword') {
      checkPasswordPolicies(e.target.value);
    }
    void schema.isValid(newValues).then((valid) => {
      setIsButtonDisabled(!valid);
    });
  };

  const resetFormState = () => {
    setIsButtonDisabled(true);
    setConditionsMet(DEFAULT_CONDITIONS);
  };

  useEffect(() => {
    // Resets component data when modal is closed
    if (!isOpen) resetFormState();
  }, [isOpen]);

  const onSubmit = async (
    values: FormValues,
    { setErrors, setStatus, setSubmitting }: FormikHelpers<FormValues>
  ) => {
    const { newPassword } = values;
    await changePassword(
      { new: newPassword, current: currentPassword },
      {
        onSuccess: () => {
          setStatus({ success: true });
          onSuccess();
          onClose();
        },
        onError: (err: ServerErrorResponse) => {
          setErrors({
            reEnteredPassword: getAuthErrorMessage(err),
          });
        },
        onSettled: () => {
          setSubmitting(false);
        },
      }
    );
  };

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
          <Typography variant='h1'>Change password</Typography>
          <CloseIcon handleClick={onClose} />
        </Grid>
        <Typography variant='subtitle1' sx={{ marginY: 24 }}>
          Please enter the new password.
        </Typography>
        <Formik<FormValues>
          initialValues={{
            newPassword: '',
            reEnteredPassword: '',
            submit: null,
          }}
          validationSchema={schema}
          innerRef={ref}
          onSubmit={onSubmit}
        >
          {({
            values,
            errors,
            isSubmitting,
            touched,
            handleChange,
            handleSubmit,
            handleBlur,
            setFieldTouched,
          }) => (
            <form noValidate onSubmit={handleSubmit} style={{ width: '100%' }}>
              <PasswordTooltip
                arrow
                disableHoverListener
                placement='top-start'
                title={
                  <>
                    <Typography fontWeight='500'>Your password must have:</Typography>
                    <ChecklistItem active={conditionsMet[CONDITION_KEYS.LENGTH]}>
                      4 or more characters
                    </ChecklistItem>
                  </>
                }
              >
                <PasswordTextField
                  name='newPassword'
                  error={!!(touched.newPassword && errors.newPassword)}
                  fullWidth
                  id='new-password-input-with-icon-textfield'
                  placeholder='New password'
                  onChange={(e) => {
                    handleChange(e);
                    onInputChange(e, values);
                  }}
                  onBlur={(e) => {
                    handleBlur(e);
                    onInputChange(e, values);
                  }}
                  type='password'
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position='start'>
                        <PasswordIcon invalid={!!(touched.newPassword && errors.newPassword)} />
                      </InputAdornment>
                    ),
                  }}
                  value={values.newPassword}
                  variant='outlined'
                />
              </PasswordTooltip>
              {errors.newPassword && touched.newPassword && (
                <Typography variant='error'>
                  <>{errors.newPassword}</>
                </Typography>
              )}
              <Box sx={{ height: 24 }} />
              <PasswordTextField
                name='reEnteredPassword'
                error={!!(touched.reEnteredPassword && errors.reEnteredPassword)}
                fullWidth
                id='re-entered-new-password-input-with-icon-textfield'
                placeholder='Re-enter new password'
                onChange={(e) => {
                  setFieldTouched('reEnteredPassword');
                  handleChange(e);
                  onInputChange(e, values);
                }}
                onBlur={(e) => {
                  handleBlur(e);
                  onInputChange(e, values);
                }}
                type='password'
                InputProps={{
                  startAdornment: (
                    <InputAdornment position='start'>
                      <PasswordIcon
                        invalid={!!(touched.reEnteredPassword && errors.reEnteredPassword)}
                      />
                    </InputAdornment>
                  ),
                }}
                value={values.reEnteredPassword}
                variant='outlined'
              />
              {errors.reEnteredPassword && touched.reEnteredPassword && (
                <Typography variant='error'>
                  <>{errors.reEnteredPassword}</>
                </Typography>
              )}
              {errors.submit && (
                <Typography variant='error'>
                  <>{errors.submit}</>
                </Typography>
              )}
              <Button
                type='submit'
                variant='contained'
                sx={{ marginTop: '24px' }}
                fullWidth
                disabled={
                  !!(errors.submit || errors.newPassword || errors.reEnteredPassword) ||
                  isSubmitting ||
                  isButtonDisabled
                }
              >
                Confirm
              </Button>
            </form>
          )}
        </Formik>
      </StyledModalContainer>
    </Modal>
  );
};

export default ChangePasswordModal;
