import {
  addBaseUrl,
  addCorrelationId,
  addEmulatorBaseUrl,
  injectAuthorization,
  refreshMechanism,
} from '@/utils/httpClient/interceptors';
import axios from 'axios';

// Used for all requests that require authentication and has automatic token refresh mechanism
const httpClient = axios.create();

httpClient.interceptors.request.use(addCorrelationId);
httpClient.interceptors.request.use(addBaseUrl);
httpClient.interceptors.request.use(injectAuthorization);
httpClient.interceptors.response.use((response) => response, refreshMechanism);

// Used for all requests that require authentication with emulator as base URL
const emulatorClient = axios.create();

emulatorClient.interceptors.request.use(addCorrelationId);
emulatorClient.interceptors.request.use(addEmulatorBaseUrl);
emulatorClient.interceptors.response.use((response) => response, refreshMechanism);

// Used for auth requests that do not require authentication
const authClient = axios.create();

authClient.interceptors.request.use(addCorrelationId);
authClient.interceptors.request.use(addBaseUrl);

// Used for logout requests that requires authentication but not refresh mechanism
const logoutClient = axios.create();

logoutClient.interceptors.request.use(addCorrelationId);
logoutClient.interceptors.request.use(addBaseUrl);
logoutClient.interceptors.request.use(injectAuthorization);

export { httpClient, emulatorClient, authClient, logoutClient };
