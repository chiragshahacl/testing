import { AxiosError } from 'axios';

type ErrorResponse = {
  detail: string;
};

export type ServerErrorResponse = AxiosError<ErrorResponse>;
