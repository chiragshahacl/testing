/**
 * Interceptors are functions that are called before the request is sent to
 * the server or after the response is received.
 * They are used to modify the request or the response.
 *
 * The following interceptors are used in this project:
 * - addCorrelationId: adds a unique identifier to the request headers
 * - addBaseUrl: adds the base URL to the request
 * - addEmulatorBaseUrl: adds the emulator base URL to the request
 * - injectAuthorization: adds the access token to the request headers
 * - refreshMechanism: refreshes the access token if it is expired
 *
 */

import { refreshTokenRequest } from '@/api/authApi';
import { httpClient } from '@/utils/httpClient/httpClient';
import { isTokenValid } from '@/utils/jwtToken';
import { getCachedRuntimeConfig } from '@/utils/runtime';
import { STORAGE_KEYS } from '@/utils/storage';
import { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { v4 as uuidv4 } from 'uuid';

export const redirectToLogin = () => {
  localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
  localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
  window.dispatchEvent(new Event('logout'));
  window.location.href = '/';
};

export const injectAuthorization = (config: InternalAxiosRequestConfig) => {
  const accessToken = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN) as string;

  config.headers['Authorization'] = `Bearer ${accessToken}`;

  return config;
};

export const addCorrelationId = (
  config: InternalAxiosRequestConfig
): InternalAxiosRequestConfig => {
  const correlationId = uuidv4();
  config.headers['x-correlation-id'] = correlationId;

  return config;
};

export const addBaseUrl = (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
  const APP_URL = getCachedRuntimeConfig().APP_URL;
  config.baseURL = APP_URL + '/';
  return config;
};

export const addEmulatorBaseUrl = (
  config: InternalAxiosRequestConfig
): InternalAxiosRequestConfig => {
  const runtimeConfig = getCachedRuntimeConfig();
  config.baseURL = runtimeConfig.EMULATOR_URL || runtimeConfig.APP_URL;
  return config;
};

export const refreshMechanism = async (error: AxiosError): Promise<AxiosResponse> => {
  const originalRequest = error.config;

  if (error.response && (error.response.status === 401 || error.response.status === 403)) {
    const refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);

    if (refreshToken && isTokenValid(refreshToken.toString())) {
      try {
        const response = await refreshTokenRequest({ refresh: refreshToken.toString() });
        if (originalRequest && response.data.access) {
          localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, response.data.access);
          originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
          return httpClient(originalRequest);
        } else {
          redirectToLogin();
        }
      } catch (e) {
        redirectToLogin();
      }
    } else {
      redirectToLogin();
    }
  }
  return Promise.reject(error);
};
