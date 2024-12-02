import { Metrics } from '@/types/metrics';
import { DisplayVitalsRange } from '@/types/patientMonitor';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import * as React from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import { METRIC_INTERNAL_CODES, RANGES_CODES } from '@/utils/metricCodes';
import { ERROR_VALUE } from '@/constants';
import { AlarmLimitTableColumnData } from '@/types/table';
import { openSansFont } from '@/utils/fonts';
import { Theme } from '@mui/material';

const columns: AlarmLimitTableColumnData[] = [
  {
    width: 160,
    label: 'Vital',
    dataKey: 'name',
  },
  {
    width: 160,
    label: 'Unit',
    dataKey: 'unit',
  },
  {
    width: 160,
    label: 'Low Limit',
    dataKey: 'low',
  },
  {
    width: 160,
    label: 'High limit',
    dataKey: 'high',
  },
];

interface VitalManagementTabProps {
  alertThresholds: Record<string, DisplayVitalsRange>;
  metrics?: Metrics;
}

const VitalManagementTab = ({ alertThresholds, metrics = {} }: VitalManagementTabProps) => {
  const rows = [
    {
      name: 'HR',
      high: alertThresholds[RANGES_CODES.HR]?.upperLimit || ERROR_VALUE,
      low: alertThresholds[RANGES_CODES.HR]?.lowerLimit || ERROR_VALUE,
      unit: metrics[METRIC_INTERNAL_CODES.HR]?.unit || 'bpm',
    },
    {
      name: 'SpO2',
      high: alertThresholds[RANGES_CODES.SPO2]?.upperLimit || ERROR_VALUE,
      low: alertThresholds[RANGES_CODES.SPO2]?.lowerLimit || ERROR_VALUE,
      unit: metrics[METRIC_INTERNAL_CODES.SPO2]?.unit || '%',
    },
    {
      name: 'PR',
      high: alertThresholds[RANGES_CODES.PR]?.upperLimit || ERROR_VALUE,
      low: alertThresholds[RANGES_CODES.PR]?.lowerLimit || ERROR_VALUE,
      unit: metrics[METRIC_INTERNAL_CODES.PR]?.unit || 'bpm',
    },
    {
      name: 'RR',
      high: alertThresholds[RANGES_CODES.RR]?.upperLimit || ERROR_VALUE,
      low: alertThresholds[RANGES_CODES.RR]?.lowerLimit || ERROR_VALUE,
      unit: metrics[METRIC_INTERNAL_CODES.RR_METRIC]?.unit || 'brpm',
    },
    {
      name: 'SYS',
      high: alertThresholds[RANGES_CODES.SYS]?.upperLimit || ERROR_VALUE,
      low: alertThresholds[RANGES_CODES.SYS]?.lowerLimit || ERROR_VALUE,
      unit: metrics[METRIC_INTERNAL_CODES.SYS]?.unit || 'mmHg',
    },
    {
      name: 'DIA',
      high: alertThresholds[RANGES_CODES.DIA]?.upperLimit || ERROR_VALUE,
      low: alertThresholds[RANGES_CODES.DIA]?.lowerLimit || ERROR_VALUE,
      unit: metrics[METRIC_INTERNAL_CODES.DIA]?.unit || 'mmHg',
    },
    {
      name: 'BODY TEMP',
      high: alertThresholds[RANGES_CODES.TEMPERATURE_BODY]?.upperLimit || ERROR_VALUE,
      low: alertThresholds[RANGES_CODES.TEMPERATURE_BODY]?.lowerLimit || ERROR_VALUE,
      unit:
        metrics[METRIC_INTERNAL_CODES.BODY_TEMP]?.unit ||
        metrics[METRIC_INTERNAL_CODES.CHEST_TEMP]?.unit ||
        metrics[METRIC_INTERNAL_CODES.LIMB_TEMP]?.unit ||
        '°F',
    },
    {
      name: 'SKIN TEMP',
      high: alertThresholds[RANGES_CODES.TEMPERATURE_SKIN]?.upperLimit || ERROR_VALUE,
      low: alertThresholds[RANGES_CODES.TEMPERATURE_SKIN]?.lowerLimit || ERROR_VALUE,
      unit:
        metrics[METRIC_INTERNAL_CODES.CHEST_TEMP]?.unit ||
        metrics[METRIC_INTERNAL_CODES.LIMB_TEMP]?.unit ||
        metrics[METRIC_INTERNAL_CODES.BODY_TEMP]?.unit ||
        '°F',
    },
  ];

  return (
    <Grid
      data-testid='alarm-limits-tab'
      sx={{
        backgroundColor: 'primary.dark',
        borderRadius: '16px',
        paddingY: 24,
      }}
    >
      <TableContainer>
        <Table sx={{ width: 'auto' }}>
          <TableHead>
            <TableRow>
              {columns.map((column) => (
                <TableCell
                  key={column.dataKey}
                  align='left'
                  sx={{
                    width: column.width,
                    padding: (theme) => theme.spacing(13, 8),
                  }}
                >
                  <Typography className={openSansFont.className} variant='h6' lineHeight='24px'>
                    {column.label}
                  </Typography>
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row) => (
              <TableRow
                key={`${row.name}`}
                data-testid={`${row.name}-${row.unit}-${row.high}-${row.low}`}
                sx={{ borderTop: (theme: Theme) => `1px solid ${theme.palette.grey[500]}` }}
              >
                {columns.map((column) => (
                  <TableCell
                    key={column.dataKey}
                    align='left'
                    sx={{
                      width: column.width,
                      padding: (theme) => theme.spacing(10, 8),
                    }}
                  >
                    <Typography className={openSansFont.className} variant='caption'>
                      {row[column.dataKey]}
                    </Typography>
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Grid>
  );
};

export default VitalManagementTab;
