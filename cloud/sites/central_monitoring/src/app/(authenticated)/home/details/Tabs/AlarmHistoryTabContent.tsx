import * as React from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { openSansFont } from '@/utils/fonts';
import { Theme } from '@mui/material';
import { AlarmHistoryTableColumnData } from '@/types/table';
import { formatCellData } from '@/utils/tableDataFormatter';
import { AlarmRecord } from '@/types/alerts';

const columns: AlarmHistoryTableColumnData[] = [
  {
    width: 213,
    label: 'Type',
    dataKey: 'type',
  },
  {
    width: 213,
    label: 'Date',
    dataKey: 'date',
  },
  {
    width: 213,
    label: 'Time',
    dataKey: 'time',
  },
  {
    width: 213,
    label: 'Priority',
    dataKey: 'priority',
  },
  {
    width: 359,
    label: 'Alarm Message',
    dataKey: 'message',
  },
  {
    width: 213,
    label: 'Duration',
    dataKey: 'duration',
  },
];

interface AlarmHistoryTabProps {
  alarmHistory: AlarmRecord[];
}

const AlarmHistoryTabContent = ({ alarmHistory }: AlarmHistoryTabProps) => (
  <Grid
    data-testid='alarm-history-tab'
    sx={{
      backgroundColor: (theme) => theme.palette.primary.dark,
      padding: (theme) => theme.spacing(24, 0, 0, 0),
      height: '77vh',
    }}
  >
    <TableContainer sx={{ maxHeight: '66vh' }}>
      <Table stickyHeader aria-label='sticky table' sx={{ width: '100%' }}>
        <TableHead sx={{ borderBottom: (theme: Theme) => `1px solid ${theme.palette.grey[500]}` }}>
          {columns.map((column) => (
            <TableCell
              key={column.dataKey}
              variant='head'
              align='left'
              sx={{
                width: column.width,
                backgroundColor: (theme) => theme.palette.primary.dark,
                whiteSpace: 'pre-wrap',
                wordWrap: 'break-word',
                padding: (theme) => theme.spacing(13, 8),
              }}
            >
              <Typography className={openSansFont.className} variant='h6'>
                {column.label}
              </Typography>
            </TableCell>
          ))}
        </TableHead>
        <TableBody>
          {alarmHistory.map((row) => (
            <TableRow
              key={`${row.date}:${row.time}`}
              sx={{ borderBottom: (theme: Theme) => `1px solid ${theme.palette.grey[500]}` }}
            >
              {columns.map((column) => (
                <TableCell
                  key={column.dataKey}
                  align='left'
                  sx={{
                    width: column.width,
                    whiteSpace: 'pre-wrap',
                    wordWrap: 'break-word',
                    padding: (theme) => theme.spacing(10, 8),
                    borderTop: (theme: Theme) => `1px solid ${theme.palette.grey[500]}`,
                  }}
                >
                  {formatCellData(column.dataKey, row[column.dataKey])}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  </Grid>
);

export default AlarmHistoryTabContent;
