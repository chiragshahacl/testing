import { FormikProps } from 'formik';

export type FormValues = {
  password: string;
  submit: boolean | null;
};

export type FormReference = FormikProps<FormValues>;
