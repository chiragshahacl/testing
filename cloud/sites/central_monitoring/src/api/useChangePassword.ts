import { ServerErrorResponse } from '@/types/response';
import { httpClient } from '@/utils/httpClient';
import { useMutation } from '@tanstack/react-query';
import { AxiosResponse } from 'axios';

export type ChangePasswordRequest = {
  current: string;
  new: string;
};

type ChangePasswordResponse = null;

const changePassword = async (
  data: ChangePasswordRequest
): Promise<AxiosResponse<ChangePasswordResponse>> => {
  return httpClient.post('/web/auth/change-password', data);
};

export const useChangePassword = () => {
  const { mutateAsync, ...rest } = useMutation<
    AxiosResponse<ChangePasswordResponse>,
    ServerErrorResponse,
    ChangePasswordRequest
  >({
    mutationFn: changePassword,
    mutationKey: ['change-password'],
  });
  return { changePassword: mutateAsync, ...rest };
};
