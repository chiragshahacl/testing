import moment from 'moment';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import { Formik, FormikProps } from 'formik';
import React, { ChangeEvent, useEffect, useRef, useState } from 'react';
import * as Yup from 'yup';
import EHRSearchField from './EHRSearchField';
import {
  EHRQuickAdmitFormInitialData,
  EHRQuickAdmitFormValues,
} from '../EHRQuickAdmitFormController';
import { SelectChangeEvent } from '@mui/material/Select';
import {
  DATE_FORMAT,
  DATE_FORMAT_ERROR_MESSAGE,
  NAME_FORMAT_ERROR_MESSAGE,
  NAME_REGEX,
} from '@/utils/ehr';
import Typography from '@mui/material/Typography';

interface EHRQuickAdmitFormProps {
  searchHandler: (values: EHRQuickAdmitFormValues) => void;
  initialData?: EHRQuickAdmitFormInitialData;
  onBack: () => void;
}

interface QuickAdmitValues {
  firstName: string;
  lastName: string;
  dob: string;
  [x: string]: string | boolean | null | undefined;
}

const EHRQuickAdmitForm = ({ initialData, searchHandler, onBack }: EHRQuickAdmitFormProps) => {
  const [isButtonDisabled, setIsButtonDisabled] = useState(true);
  const [values, setValues] = useState<QuickAdmitValues>({
    firstName: initialData?.firstName || '',
    lastName: initialData?.lastName || '',
    dob: initialData?.dob || '',
  });
  const formRef = useRef<FormikProps<EHRQuickAdmitFormValues> | null>(null);

  const quickAdmitSchema = Yup.object().shape({
    firstName: Yup.string()
      .matches(NAME_REGEX, NAME_FORMAT_ERROR_MESSAGE)
      .required('First name is required.'),
    lastName: Yup.string()
      .matches(NAME_REGEX, NAME_FORMAT_ERROR_MESSAGE)
      .required('Last name is required.'),
    dob: Yup.string().when({
      is: (exists: boolean) => !!exists,
      then: (rule) =>
        rule.test(
          'correct_dob_format',
          'Please enter a valid date',
          (date) => date === DATE_FORMAT || moment(date, DATE_FORMAT, true).isValid()
        ),
    }),
    sex: Yup.string(),
  });

  const onInputChange = (name: string, value: string) => {
    const updatedValues: QuickAdmitValues = values;
    updatedValues[name] = value;
    void quickAdmitSchema.isValid(updatedValues).then((valid) => {
      const newErrors = { ...formRef.current?.errors };
      if (updatedValues.firstName && !updatedValues.firstName.match(NAME_REGEX)) {
        newErrors.firstName = NAME_FORMAT_ERROR_MESSAGE;
      } else {
        delete newErrors.firstName;
      }
      if (updatedValues.lastName && !updatedValues.lastName.match(NAME_REGEX)) {
        newErrors['lastName'] = NAME_FORMAT_ERROR_MESSAGE;
      } else {
        delete newErrors.lastName;
      }
      if (updatedValues.dob && !moment(updatedValues.dob, DATE_FORMAT, true).isValid()) {
        newErrors['dob'] = DATE_FORMAT_ERROR_MESSAGE;
      } else {
        delete newErrors.dob;
      }
      formRef.current?.setErrors(newErrors);
      setIsButtonDisabled(!valid);
    });
    setValues((val) => ({ ...val, [name]: value }));
  };

  const onSubmit = () => {
    searchHandler({ ...values });
  };

  useEffect(() => {
    setIsButtonDisabled(!(initialData?.firstName && initialData?.lastName));
  }, [initialData]);

  return (
    <Formik<EHRQuickAdmitFormValues>
      initialValues={{
        firstName: initialData?.firstName || '',
        lastName: initialData?.lastName || '',
        dob: '',
        sex: '',
        submit: null,
      }}
      innerRef={formRef}
      onSubmit={onSubmit}
    >
      {({ values, errors, isSubmitting, handleChange, handleSubmit }) => (
        <form
          noValidate
          onSubmit={handleSubmit}
          onReset={onBack}
          style={{ display: 'flex', flexDirection: 'column' }}
        >
          <EHRSearchField
            name='firstName'
            title={'First name'}
            id={'first-name-textfield'}
            onChange={(e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
              handleChange(e);
              onInputChange(e.target.name, e.target.value);
            }}
            value={values.firstName}
            error={errors.firstName}
            required
          />
          <EHRSearchField
            name='lastName'
            title={'Last name'}
            id={'last-name-textfield'}
            onChange={(e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
              handleChange(e);
              onInputChange(e.target.name, e.target.value);
            }}
            value={values.lastName}
            error={errors.lastName}
            required
          />
          <EHRSearchField
            name='dob'
            title={'DOB'}
            id={'dob-textfield'}
            onDateChange={(name: string, value: string) => {
              if (name) {
                if (value === DATE_FORMAT) {
                  onInputChange(name, '');
                } else {
                  onInputChange(name, value);
                }
              }
            }}
            value={values.dob}
            error={errors.dob}
            type='dob'
            placeholder={DATE_FORMAT}
          />
          <EHRSearchField
            name='sex'
            title={'Sex'}
            id={'sex-textfield'}
            onSelect={(e: SelectChangeEvent) => {
              handleChange(e);
              onInputChange(e.target.name, e.target.value);
            }}
            value={values.sex}
            type='select'
          />
          {errors.submit && (
            <Box marginTop={24} alignSelf='center'>
              <Typography variant='error'>
                <>{errors.submit}</>
              </Typography>
            </Box>
          )}
          <Box height={52} />
          <Box display='flex' flexDirection='row' gap='24px' width='100%'>
            <Button
              data-testid='back-button'
              type='reset'
              variant='outlined'
              sx={{ height: '48px', flex: 1 }}
            >
              Back
            </Button>
            <Button
              data-testid='search-button'
              type='submit'
              variant='contained'
              disabled={errors.submit ? true : isSubmitting || isButtonDisabled}
              sx={{ height: '48px', flex: 1 }}
            >
              Quick admit
            </Button>
          </Box>
        </form>
      )}
    </Formik>
  );
};

export default EHRQuickAdmitForm;
