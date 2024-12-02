import { usePatientMonitors } from '@/api/usePatientMonitors';
import { CheckedIcon, UncheckedIcon } from '@/components/icons/CheckIcon';
import { BedType } from '@/types/bed';
import { findAssociatedMonitor } from '@/utils/patientUtils';
import Checkbox from '@mui/material/Checkbox';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell, { TableCellProps } from '@mui/material/TableCell';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';
import { alpha, styled } from '@mui/material/styles';
import React from 'react';

const StickyTableCell = styled(TableCell)<TableCellProps>(({ theme }) => ({
  left: 0,
  top: 0,
  bottom: 36,
  position: 'sticky',
  zIndex: 100,
  backgroundColor: theme.palette.secondary.main,
}));

interface TableListWithCheckboxProps {
  data: BedType[];
  checkedBeds: BedType[];
  handleCheck: (bedInfo: BedType) => void;
  handleUncheck: (bedInfo: BedType) => void;
}

const TableListWithCheckbox = ({
  data,
  checkedBeds,
  handleCheck,
  handleUncheck,
}: TableListWithCheckboxProps) => {
  const patientMonitors = usePatientMonitors();

  const handleSelectionChange = (event: React.ChangeEvent<HTMLInputElement>, bedInfo: BedType) => {
    if (event.target.checked) {
      handleCheck(bedInfo);
    } else {
      handleUncheck(bedInfo);
    }
  };

  return (
    <Table sx={{ whiteSpace: 'nowrap' }}>
      <TableBody>
        <TableRow>
          <StickyTableCell
            color='secondary.main'
            sx={{
              padding: 0,
              margin: 0,
              width: 48,
              borderBottom: 'none',
            }}
          />
          <StickyTableCell
            sx={{
              padding: (theme) => theme.spacing(0, 16, 0, 0),
            }}
          >
            <Typography variant='h6' color={(theme) => theme.palette.grey[600]}>
              Bed ID
            </Typography>
          </StickyTableCell>
          <StickyTableCell
            sx={{
              padding: 0,
              margin: 0,
              borderBottom: 'none',
            }}
          >
            <Typography variant='h6' color={(theme) => theme.palette.grey[600]}>
              Patient Monitor ID
            </Typography>
          </StickyTableCell>
        </TableRow>
        {data.map((bed: BedType) => (
          <TableRow key={bed.bedNo}>
            <TableCell sx={{ padding: 0, margin: 0, width: 48, borderBottom: 'none' }}>
              <Checkbox
                icon={
                  <UncheckedIcon
                    disabled={
                      checkedBeds.length === 16 && !checkedBeds.find((b) => b.id === bed.id)
                    }
                  />
                }
                checkedIcon={<CheckedIcon />}
                disableRipple
                onChange={(e) => handleSelectionChange(e, bed)}
                checked={!!checkedBeds.find((b) => b.bedNo === bed.bedNo)}
                disabled={checkedBeds.length === 16 && !checkedBeds.find((b) => b.id === bed.id)}
                inputProps={{ 'aria-label': `${bed.bedNo}-checkbox` }}
              />
            </TableCell>
            <TableCell sx={{ padding: (theme) => theme.spacing(0, 16, 0, 0) }}>
              <Typography
                variant='body2'
                color={(theme) =>
                  checkedBeds.length === 16 && !checkedBeds.find((b) => b.id === bed.id)
                    ? alpha(theme.palette.grey[600], 0.2)
                    : theme.palette.grey[600]
                }
              >
                {bed.bedNo}
              </Typography>
            </TableCell>
            <TableCell sx={{ padding: 0, margin: 0, borderBottom: 'none' }}>
              <Typography
                variant='body1'
                color={(theme) =>
                  checkedBeds.length === 16 && !checkedBeds.find((b) => b.id === bed.id)
                    ? alpha(theme.palette.grey[600], 0.2)
                    : theme.palette.grey[600]
                }
              >
                {findAssociatedMonitor(bed.id, patientMonitors.data, '-')}
              </Typography>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};

export default TableListWithCheckbox;
