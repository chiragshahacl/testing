import { ServerErrorResponse } from '@/types/response';
import { authClient } from '@/utils/httpClient';
import { useMutation } from '@tanstack/react-query';
import { AxiosResponse } from 'axios';

type PasswordValidationRequest = {
  password: string;
};

type PasswordValidationResponse = null;

const validatePassword = async (
  data: PasswordValidationRequest,
  endpoint: string
): Promise<AxiosResponse<PasswordValidationResponse>> => {
  return authClient.post<PasswordValidationResponse>(endpoint, data);
};

type UsePasswordValidationProps = {
  endpoint: string;
  mutationKey: string;
};

export const usePasswordValidator = ({ endpoint, mutationKey }: UsePasswordValidationProps) => {
  const { mutateAsync, ...rest } = useMutation<
    AxiosResponse<PasswordValidationResponse>,
    ServerErrorResponse,
    PasswordValidationRequest
  >({
    mutationFn: (data: PasswordValidationRequest) => validatePassword(data, endpoint),
    mutationKey: [mutationKey],
  });

  return { validate: mutateAsync, ...rest };
};

export const usePasswordValidation = () =>
  usePasswordValidator({
    endpoint: '/web/auth/token',
    mutationKey: 'validate-password',
  });

export const useTechnicalPasswordValidation = () =>
  usePasswordValidator({
    endpoint: '/web/auth/technical/token',
    mutationKey: 'validate-technical-password',
  });
