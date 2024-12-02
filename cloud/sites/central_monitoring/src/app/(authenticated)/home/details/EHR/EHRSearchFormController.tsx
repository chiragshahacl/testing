import Typography from '@mui/material/Typography';
import React, { useState } from 'react';
import EHRSearchFormByName from './components/EHRSearchFormByName';
import EHRSearchFormById from './components/EHRSearchFormById';
import Grid from '@mui/material/Grid';
import { openSansFont } from '@/utils/fonts';
import styled from '@emotion/styled';

const SwitchButton = styled(Grid)(() => ({
  display: 'flex',
  flex: 1,
  flexDirection: 'row',
  justifyContent: 'center',
  padding: '12px 29px',
  width: '158px',
  borderRadius: '42px',
}));

export type SearchByNameFormValues = {
  firstName: string;
  lastName: string;
  dob?: string;
  submit: boolean | null;
};

export type SearchByIdFormValues = {
  patientPrimaryIdentifier: string;
  submit: boolean | null;
};

interface EHRSearchFormControllerProps {
  searchHandler: (values: SearchByNameFormValues | SearchByIdFormValues) => Promise<boolean>;
  onBack: () => void;
  dismissNoPatientError: () => void;
  errorMessage: string;
}

enum SearchBy {
  ID = 'ID',
  NAME = 'NAME',
}

const EHRSearchFormController = ({
  searchHandler,
  onBack,
  dismissNoPatientError,
  errorMessage,
}: EHRSearchFormControllerProps) => {
  const [searchBy, setSearchBy] = useState<SearchBy>(SearchBy.ID);

  const onChangeSearchBy = () => {
    dismissNoPatientError();
    setSearchBy((previousSearchBy) => {
      if (previousSearchBy === SearchBy.NAME) return SearchBy.ID;
      return SearchBy.NAME;
    });
  };

  return (
    <>
      <Grid
        display='flex'
        flexDirection='row'
        justifyContent='flex-start'
        sx={{
          borderRadius: 42,
          border: '2px solid #A8ADB3',
          width: '22%',
        }}
        onClick={onChangeSearchBy}
      >
        <SwitchButton
          sx={{
            backgroundColor: () => (searchBy === SearchBy.ID ? 'background.active' : 'transparent'),
            marginRight: '-16px',
          }}
        >
          <Typography
            color={(theme) =>
              searchBy === SearchBy.ID ? theme.palette.common.white : theme.palette.grey[800]
            }
            sx={{
              marginLeft: 8,
              fontFamily: openSansFont.style.fontFamily,
              fontSize: 16,
              fontWeight: 700,
            }}
          >
            ID
          </Typography>
        </SwitchButton>
        <SwitchButton
          sx={{
            backgroundColor: searchBy !== SearchBy.ID ? 'background.active' : 'transparent',
            marginLeft: '-16px',
          }}
        >
          <Typography
            color={(theme) =>
              searchBy !== SearchBy.ID ? theme.palette.common.white : theme.palette.grey[800]
            }
            sx={{
              marginLeft: 8,
              fontFamily: openSansFont.style.fontFamily,
              fontSize: 16,
              fontWeight: 700,
            }}
          >
            NAME
          </Typography>
        </SwitchButton>
      </Grid>
      {searchBy === SearchBy.NAME ? (
        <EHRSearchFormByName
          searchHandler={searchHandler}
          onBack={onBack}
          errorMessage={errorMessage}
        />
      ) : (
        <EHRSearchFormById
          searchHandler={searchHandler}
          onBack={onBack}
          errorMessage={errorMessage}
        />
      )}
    </>
  );
};

export default EHRSearchFormController;
