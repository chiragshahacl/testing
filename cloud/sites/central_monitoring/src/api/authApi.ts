import { authClient } from '@/utils/httpClient';
import { AxiosResponse } from 'axios';

type RefreshTokenRequest = {
  refresh: string;
};

type RefreshTokenResponse = {
  access: string;
};

const refreshTokenRequest = async (
  data: RefreshTokenRequest
): Promise<AxiosResponse<RefreshTokenResponse>> => {
  return authClient.post<RefreshTokenResponse>('/web/auth/token/refresh', data);
};

export { refreshTokenRequest };
