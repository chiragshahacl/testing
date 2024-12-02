import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import { Formik, FormikProps } from 'formik';
import React, { ChangeEvent, useRef, useState } from 'react';
import * as Yup from 'yup';
import { SearchByIdFormValues } from '../EHRSearchFormController';
import EHRSearchField from './EHRSearchField';
import Typography from '@mui/material/Typography';

interface EHRSearchFormByIdProps {
  searchHandler: (values: SearchByIdFormValues) => Promise<boolean>;
  onBack: () => void;
  errorMessage: string;
}

const EHRSearchFormById = ({ searchHandler, onBack, errorMessage }: EHRSearchFormByIdProps) => {
  const [isButtonDisabled, setIsButtonDisabled] = useState(true);
  const [byIdValues, setByIdValues] = useState({ patientPrimaryIdentifier: '' });
  const formRefSearchById = useRef<FormikProps<SearchByIdFormValues> | null>(null);

  const searchByIDSchema = Yup.object().shape({
    patientPrimaryIdentifier: Yup.string().required('ID is required.'),
  });

  const onByIDInputChange = (e: React.ChangeEvent<HTMLTextAreaElement | HTMLInputElement>) => {
    const updatedValues: Record<string, string> = byIdValues;
    updatedValues[e.target.name] = e.target.value;
    void searchByIDSchema.isValid(updatedValues).then((valid) => {
      setIsButtonDisabled(!valid);
    });
    setByIdValues((val) => ({ ...val, [e.target.name]: e.target.value }));
  };

  const onSubmit = async () => {
    const success = await searchHandler({ ...byIdValues, submit: null });
    if (success) return true;
    else {
      formRefSearchById.current?.setErrors({ submit: 'No results found' });
      return false;
    }
  };

  return (
    <Formik<SearchByIdFormValues>
      initialValues={{
        patientPrimaryIdentifier: '',
        submit: null,
      }}
      innerRef={formRefSearchById}
      onSubmit={onSubmit}
    >
      {({ errors, isSubmitting, handleChange, handleSubmit }) => (
        <form
          noValidate
          onSubmit={handleSubmit}
          onReset={onBack}
          style={{ display: 'flex', flexDirection: 'column' }}
        >
          <EHRSearchField
            name='patientPrimaryIdentifier'
            title='Patient ID'
            id='patient-id-textfield'
            onChange={(e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
              handleChange(e);
              onByIDInputChange(e);
            }}
            required
          />
          <Box height={52} />
          {errors.submit && (
            <Box marginTop={24} textAlign='center' width='70%'>
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
  );
};

export default EHRSearchFormById;
