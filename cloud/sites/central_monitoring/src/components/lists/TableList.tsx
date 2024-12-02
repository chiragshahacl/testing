import { usePatientMonitors } from '@/api/usePatientMonitors';
import { BedType } from '@/types/bed';
import { openSansFont } from '@/utils/fonts';
import { findAssociatedMonitor } from '@/utils/patientUtils';
import { styled } from '@mui/material/styles';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';

const StyledShortTableCell = styled(TableCell)(({ theme }) => ({
  padding: theme.spacing(0, 48, 0, 0),
  margin: 0,
  width: '20%',
}));
const StyledLongTableCell = styled(TableCell)(() => ({ padding: 0, margin: 0, width: '80%' }));

interface TableListProps {
  data: BedType[];
}

const TableList = ({ data }: TableListProps) => {
  const patientMonitors = usePatientMonitors();

  return (
    <Table sx={{ whiteSpace: 'nowrap' }}>
      <TableHead>
        <TableRow>
          <StyledShortTableCell>
            <Typography variant='h5'>Bed ID</Typography>
          </StyledShortTableCell>
          <StyledLongTableCell>
            <Typography variant='h5'>Patient monitor ID</Typography>
          </StyledLongTableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {data?.map((bed: BedType) => (
          <TableRow key={bed.bedNo}>
            <StyledShortTableCell>
              <Typography
                color={(theme) => theme.palette.grey[600]}
                variant='body2'
                sx={{ fontFamily: openSansFont.style.fontFamily }}
              >
                {bed.bedNo}
              </Typography>
            </StyledShortTableCell>
            <StyledLongTableCell>
              <Typography
                color={(theme) => theme.palette.grey[600]}
                variant='body2'
                sx={{ fontFamily: openSansFont.style.fontFamily }}
              >
                {findAssociatedMonitor(bed.id, patientMonitors.data)}
              </Typography>
            </StyledLongTableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};

export default TableList;
