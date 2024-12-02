import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import { Formik, FormikProps } from 'formik';
import React, { ChangeEvent, useRef, useState } from 'react';
import * as Yup from 'yup';
import EHRSearchField from './EHRSearchField';
import AgeWarningModal from '@/components/modals/patientSubmission/AgeWarningModal';
import { checkAgeLessThanYears } from '@/utils/ageCheck';
import {
  DATE_FORMAT,
  DATE_FORMAT_ERROR_MESSAGE,
  NAME_FORMAT_ERROR_MESSAGE,
  NAME_REGEX,
} from '@/utils/ehr';
import moment from 'moment';
import Typography from '@mui/material/Typography';

type SearchByNameFormValues = {
  firstName: string;
  lastName: string;
  dob?: string;
  submit: boolean | null;
};

interface EHRSearchFormByNameProps {
  searchHandler: (values: SearchByNameFormValues) => Promise<boolean>;
  onBack: () => void;
  errorMessage: string;
}

const EHRSearchFormByName = ({ searchHandler, onBack, errorMessage }: EHRSearchFormByNameProps) => {
  const [isButtonDisabled, setIsButtonDisabled] = useState(true);
  const [showAgeWarning, setShowAgeWarning] = useState(false);
  const [byNameValues, setByNamesValues] = useState({ firstName: '', lastName: '', dob: '' });
  const formRefSearchByName = useRef<FormikProps<SearchByNameFormValues> | null>(null);

  const searchByNameSchema = Yup.object().shape({
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
  });

  const onByNameInputChange = (name: string, value: string) => {
    const updatedValues: Record<string, string> = byNameValues;
    updatedValues[name] = value;
    void searchByNameSchema.isValid(updatedValues).then((valid) => {
      const newErrors = { ...formRefSearchByName.current?.errors };
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
      formRefSearchByName.current?.setErrors(newErrors);
      setIsButtonDisabled(!valid);
    });
    setByNamesValues((val) => ({ ...val, [name]: value }));
  };

  const checkAge = async () => {
    if (byNameValues.dob && checkAgeLessThanYears(byNameValues.dob, 12)) setShowAgeWarning(true);
    else {
      setShowAgeWarning(false);
      await onSubmit();
    }
    return true;
  };

  const onSubmit = async () => {
    const success = await searchHandler({ ...byNameValues, submit: null });
    if (!success) formRefSearchByName.current?.setErrors({ submit: 'No results found' });
  };

  return (
    <>
      <AgeWarningModal
        isOpen={showAgeWarning}
        onConfirm={async () => {
          setShowAgeWarning(false);
          await onSubmit();
        }}
        onCancel={() => {
          setShowAgeWarning(false);
        }}
      />
      <Formik<SearchByNameFormValues>
        initialValues={{
          firstName: '',
          lastName: '',
          submit: null,
        }}
        innerRef={formRefSearchByName}
        onSubmit={checkAge}
      >
        {({ errors, isSubmitting, handleChange, handleSubmit }) => (
          <form
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
                onByNameInputChange(e.target.name, e.target.value);
              }}
              error={errors.firstName}
              required
            />
            <EHRSearchField
              name='lastName'
              title={'Last name'}
              id={'last-name-textfield'}
              onChange={(e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
                handleChange(e);
                onByNameInputChange(e.target.name, e.target.value);
              }}
              error={errors.lastName}
              required
            />
            <EHRSearchField
              name='dob'
              title='DOB'
              id='dob-textfield'
              onDateChange={(name: string, value: string) => {
                if (name) {
                  if (value === DATE_FORMAT) {
                    onByNameInputChange(name, '');
                  } else {
                    onByNameInputChange(name, value);
                  }
                }
              }}
              error={errors.dob}
              type='dob'
              placeholder={DATE_FORMAT}
            />
            <Box height={52} />
            {errors.submit && (
              <Box marginTop={24} textAlign='center' width='70%' alignSelf='center'>
                <Typography variant='error'>
                  <>{errors.submit}</>
                </Typography>
              </Box>
            )}
            {errorMessage && (
              <Box marginTop={24} textAlign='center' width='70%' alignSelf='center'>
                <Typography variant='error'>{errorMessage}</Typography>
              </Box>
            )}
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
                Search
              </Button>
            </Box>
          </form>
        )}
      </Formik>
    </>
  );
};

export default EHRSearchFormByName;
