import { INTERVAL_VALIDATION_ERROR, PORT_VALIDATION_ERROR } from '@/constants';
import * as Yup from 'yup';

const pattern = new RegExp(
  '^((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|' + // domain name
    '((\\d{1,3}\\.){3}\\d{1,3}))$', // OR ip (v4) address
  'i'
);

export const ehrFormSchema = Yup.object().shape({
  host: Yup.string()
    .matches(pattern, 'Incorrect format. (e.g. demo.com | 127.0.0.1)')
    .required('Host is required.')
    .typeError('Incorrect format. (e.g. demo.com | 127.0.0.1)'),
  port: Yup.number()
    .integer(PORT_VALIDATION_ERROR)
    .required('Port is required.')
    .typeError(PORT_VALIDATION_ERROR),
  interval: Yup.number()
    .integer(INTERVAL_VALIDATION_ERROR)
    .min(1, INTERVAL_VALIDATION_ERROR)
    .max(100, INTERVAL_VALIDATION_ERROR)
    .required('Enter a value between 1 - 100')
    .typeError(INTERVAL_VALIDATION_ERROR),
});
