import React, { ReactElement, useMemo, useState } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import { EHRPatientType } from '@/types/patient';
import Table from '@mui/material/Table';
import TableHead from '@mui/material/TableHead';
import TableCell from '@mui/material/TableCell';
import TableRow from '@mui/material/TableRow';
import TableBody from '@mui/material/TableBody';
import Typography from '@mui/material/Typography';
import { styled } from '@mui/material/styles';
import Checkbox from '@mui/material/Checkbox';
import { SelectPatientEmptyCheckbox } from '@/components/icons/SelectPatientEmptyCheckbox';
import { SelectPatientCheckedCheckbox } from '@/components/icons/SelectPatientCheckedCheckbox';

const BigTitleTableCell = styled(TableCell)(() => ({
  width: '23.5%',
  paddingTop: 0,
  paddingBottom: '13px',
}));
const BigTableCell = styled(TableCell)(() => ({
  width: '23.5%',
  paddingTop: 0,
  paddingBottom: 0,
}));
const SmallTableCell = styled(TableCell)(() => ({
  width: '4%',
  padding: 0,
}));

const TableCustomContainer = styled(Box)`
  max-height: 70vh;
  overflow-y: scroll;

  &::-webkit-scrollbar {
    width: 4px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background-color: #d0d3d7;
    border-radius: 2px;
  }

  &::-webkit-scrollbar-thumb: hover {
    background-color: transparent;
  }
`;

const TitleText = styled(Typography)(() => ({
  fontSize: '16px',
  fontWeight: 700,
  lineHeight: '16px',
  letterSpacing: '0.02em',
}));

const FieldText = styled(Typography)(() => ({
  fontSize: '16px',
  fontWeight: '400',
  lineHeight: '21.79px',
  textAlign: 'left',
}));

interface EHRSearchResultsProps {
  submitHandler: (selectedPatient: EHRPatientType) => void;
  foundPatients: EHRPatientType[];
  onBack: () => void;
}

const EHRSearchResults = ({ submitHandler, foundPatients, onBack }: EHRSearchResultsProps) => {
  const [selectedPatientIndex, setSelectedPatientIndex] = useState<number | null>(null);

  const renderPatientLines = useMemo(() => {
    const result: ReactElement[] = [];
    foundPatients.forEach((singlePatient, index) => {
      result.push(
        <TableRow sx={{ borderTop: '1px solid #353537' }}>
          <SmallTableCell>
            <Checkbox
              checked={selectedPatientIndex === index}
              onChange={() => setSelectedPatientIndex(index)}
              icon={<SelectPatientEmptyCheckbox />}
              checkedIcon={<SelectPatientCheckedCheckbox />}
            />
          </SmallTableCell>
          <BigTableCell>
            <FieldText>{singlePatient.lastName}</FieldText>
          </BigTableCell>
          <BigTableCell>
            <FieldText>{singlePatient.firstName}</FieldText>
          </BigTableCell>
          <BigTableCell>
            <FieldText>{singlePatient.dob}</FieldText>
          </BigTableCell>
          <BigTableCell>
            <TitleText>
              <FieldText>{singlePatient.patientPrimaryIdentifier}</FieldText>
            </TitleText>
          </BigTableCell>
        </TableRow>
      );
    });
    return result;
  }, [foundPatients, selectedPatientIndex]);

  return (
    <>
      <TableCustomContainer>
        <Table>
          <TableHead>
            <TableRow>
              <SmallTableCell></SmallTableCell>
              <BigTitleTableCell>
                <TitleText>Last Name</TitleText>
              </BigTitleTableCell>
              <BigTitleTableCell>
                <TitleText>First Name</TitleText>
              </BigTitleTableCell>
              <BigTitleTableCell>
                <TitleText>DOB</TitleText>
              </BigTitleTableCell>
              <BigTitleTableCell>
                <TitleText>Patient ID</TitleText>
              </BigTitleTableCell>
            </TableRow>
          </TableHead>
          <TableBody sx={{ borderBottom: '1px solid #353537' }}>{renderPatientLines}</TableBody>
        </Table>
      </TableCustomContainer>
      <Box display='flex' flexDirection='row' gap='24px' width='100%' mt='8px'>
        <Button
          data-testid='back-button'
          type='reset'
          variant='outlined'
          sx={{ height: '48px', flex: 1 }}
          onClick={onBack}
        >
          Back
        </Button>
        <Button
          data-testid='search-button'
          type='submit'
          variant='contained'
          sx={{ height: '48px', flex: 1 }}
          onClick={() => {
            if (selectedPatientIndex && foundPatients[selectedPatientIndex])
              submitHandler(foundPatients[selectedPatientIndex]);
          }}
          disabled={selectedPatientIndex === null}
        >
          Admit Patient
        </Button>
      </Box>
    </>
  );
};

export default EHRSearchResults;
