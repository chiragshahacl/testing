import { getAuthErrorMessage } from '@/api/authErrors';
import { useLogout } from '@/api/useLogout';
import PasswordValidationModal, { FormValues } from '@/components/modals/PasswordValidationModal';
import { AUDIO_DISABLED_TIMER } from '@/constants';
import useAudioManager from '@/hooks/useAudioManager';
import usePatientData from '@/hooks/usePatientsData';
import { FormikHelpers } from 'formik';
import { useRouter } from 'next/navigation';

interface LogoutModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const LogoutModal = ({ isOpen, onClose }: LogoutModalProps) => {
  const router = useRouter();
  const { setAudioDisabledTimer, setAudioIsActive, stopAlertSound } = useAudioManager();
  const { removeSelfFromBedsDisplayGroup } = usePatientData();
  const { logout } = useLogout();

  const onSubmit = async (
    values: FormValues,
    { setErrors, setSubmitting }: FormikHelpers<FormValues>
  ) => {
    const { password } = values;
    await logout(
      { password },
      {
        onSuccess: () => {
          removeSelfFromBedsDisplayGroup();
          stopAlertSound();
          setAudioDisabledTimer(AUDIO_DISABLED_TIMER);
          setAudioIsActive(true);
          router.replace('/');
        },
        onError: (err) => {
          setErrors({ password: getAuthErrorMessage(err) });
        },
        onSettled: () => {
          setSubmitting(false);
        },
      }
    );
  };

  return <PasswordValidationModal isOpen={isOpen} onSubmit={onSubmit} onClose={onClose} />;
};

export default LogoutModal;
