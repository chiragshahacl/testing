import useSession from '@/hooks/useSession';
import { ServerErrorResponse } from '@/types/response';
import { authClient } from '@/utils/httpClient';
import { useMutation } from '@tanstack/react-query';
import { AxiosResponse } from 'axios';
import { STORAGE_KEYS } from '../utils/storage';
import { USER_TYPE } from '@/constants';

type LoginRequest = {
  password: string;
};

type LoginResponse = {
  access: string;
  refresh: string;
};

const login = async (
  data: LoginRequest,
  endpoint: string
): Promise<AxiosResponse<LoginResponse>> => {
  return authClient.post<LoginResponse>(endpoint, data);
};

type UseAuthProps = {
  endpoint: string;
  userType: USER_TYPE;
  mutationKey: string;
};

export const useAuth = ({ endpoint, userType, mutationKey }: UseAuthProps) => {
  const { setRefreshToken, setAccessToken, setIsLoggedIn, setUserType } = useSession();

  const { mutateAsync, ...rest } = useMutation<
    AxiosResponse<LoginResponse>,
    ServerErrorResponse,
    LoginRequest
  >({
    mutationFn: (data: LoginRequest) => login(data, endpoint),
    mutationKey: [mutationKey],
    onSuccess: (response) => {
      localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, response.data.access);
      localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, response.data.refresh);
      localStorage.setItem(STORAGE_KEYS.USER_TYPE, userType);
      setUserType(userType);
      setAccessToken(response.data.access);
      setRefreshToken(response.data.refresh);
      setIsLoggedIn(true);
    },
  });

  return { login: mutateAsync, ...rest };
};

export const useLogin = () =>
  useAuth({
    endpoint: '/web/auth/token',
    userType: USER_TYPE.NON_TECH,
    mutationKey: 'login',
  });

export const useTechnicalLogin = () =>
  useAuth({
    endpoint: '/web/auth/technical/token',
    userType: USER_TYPE.TECH,
    mutationKey: 'technical-login',
  });
