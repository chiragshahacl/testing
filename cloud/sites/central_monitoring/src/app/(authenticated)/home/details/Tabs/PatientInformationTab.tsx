import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { capitalize } from 'lodash';

interface PatientInfo {
  id: string;
  firstName: string;
  lastName: string;
  sex: string;
  dob: string;
}

interface InfoItemProps {
  infoKey: string;
  value: string;
}

const InfoItem = ({ infoKey, value }: InfoItemProps) => {
  return (
    <Grid item display='flex' flexDirection='row' gap='24px' sx={{ my: '17.5px', mx: '24px' }}>
      <Grid item lg={3}>
        <Typography variant='body2'>{infoKey}</Typography>
      </Grid>
      <Grid item lg={9}>
        <Typography variant='body1'>{value}</Typography>
      </Grid>
    </Grid>
  );
};

const PatientInfoTab = (patientInfo: PatientInfo) => {
  return (
    <Grid
      data-testid='patient-info-tab'
      container
      display='flex'
      flexDirection='column'
      sx={{
        backgroundColor: 'primary.dark',
        borderRadius: '16px',
      }}
    >
      <Typography variant='h2' sx={{ margin: '16px', color: 'common.white' }}>
        Demographic info
      </Typography>
      <hr color='#F2F4F6' style={{ width: '100%', height: '1px', margin: 0 }} />
      <Grid container flexDirection='column'>
        <InfoItem key='patient-id' infoKey='ID' value={patientInfo.id} />
        <InfoItem key='patient-first-name' infoKey='First name' value={patientInfo.firstName} />
        <InfoItem key='patient-last-name' infoKey='Last name' value={patientInfo.lastName} />
        <InfoItem key='patient-gender' infoKey='Sex' value={capitalize(patientInfo.sex)} />
        <InfoItem key='patient-dob' infoKey='DOB' value={patientInfo.dob} />
      </Grid>
    </Grid>
  );
};

export default PatientInfoTab;
