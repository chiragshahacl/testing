import { getAuthErrorMessage } from '@/api/authErrors';
import { usePasswordValidation } from '@/api/usePasswordValidation';
import ChangePasswordModal from '@/components/modals/ChangePasswordModal';
import PasswordChangedModal from '@/components/modals/PasswordChangedModal';
import PasswordValidationModal, { FormValues } from '@/components/modals/PasswordValidationModal';
import { ServerErrorResponse } from '@/types/response';
import { FormikHelpers } from 'formik';
import { useState } from 'react';

type ChangePasswordProps = {
  isOpen: boolean;
  onClose: () => void;
};

const ChangePassword = ({ isOpen, onClose }: ChangePasswordProps) => {
  const [currentPassword, setCurrentPassword] = useState<string | null>(null);
  const [isChangePasswordOpen, setIsChangePasswordOpen] = useState<boolean>(false);
  const [passwordChanged, setPasswordChanged] = useState<boolean>(false);
  const { validate } = usePasswordValidation();

  const onValidateSubmit = async (
    values: FormValues,
    { setErrors, setSubmitting }: FormikHelpers<FormValues>
  ) => {
    const { password } = values;
    await validate(
      { password },
      {
        onSuccess: (_, { password }) => {
          setCurrentPassword(password);
          setIsChangePasswordOpen(true);
          onClose();
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

  return (
    <>
      <PasswordValidationModal isOpen={isOpen} onClose={onClose} onSubmit={onValidateSubmit} />
      {passwordChanged ? (
        <PasswordChangedModal
          onClose={() => {
            setPasswordChanged(false);
            onClose();
          }}
        />
      ) : (
        currentPassword && (
          <ChangePasswordModal
            isOpen={isChangePasswordOpen}
            onClose={() => {
              setIsChangePasswordOpen(false);
              onClose();
            }}
            currentPassword={currentPassword}
            onSuccess={() => {
              setPasswordChanged(true);
            }}
          />
        )
      )}
    </>
  );
};

export default ChangePassword;
