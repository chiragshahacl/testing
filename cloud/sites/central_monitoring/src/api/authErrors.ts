import { requestErrors } from '@/constants';
import { ServerErrorResponse } from '@/types/response';
import { get } from 'lodash';

export const getAuthErrorMessage = (err: ServerErrorResponse) => {
  const errorMessage = get(err, 'response.data.detail');
  switch (err.response?.status) {
    case 401:
    case 422:
      return errorMessage === requestErrors.accountLocked
        ? requestErrors.tooManyAttempts
        : requestErrors.incorrectPassword;
    case 403:
    case 429:
      return requestErrors.tooManyAttempts;
    default:
      return requestErrors.serverError;
  }
};

export const getAuthErrorMessageKey = (err: ServerErrorResponse): string => {
  const errorMessage = get(err, 'response.data.detail');
  switch (err.response?.status) {
    case 401:
    case 422:
      return errorMessage === requestErrors.accountLocked
        ? 'RequestErrors.tooManyAttempts'
        : 'RequestErrors.incorrectPassword';
    case 403:
    case 429:
      return 'RequestErrors.tooManyAttempts';
    default:
      return 'RequestErrors.serverError';
  }
};
