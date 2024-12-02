import AlertList from '@/components/lists/AlertList';
import { SENSOR_CODES } from '@/types/sensor';
import { ALERT_PRIORITY, ALERT_TYPES, VITALS_ALERT_CODES } from '@/utils/metricCodes';
import Grid from '@mui/material/Grid';
import { Meta, StoryObj } from '@storybook/react';

const meta: Meta<typeof AlertList> = {
  component: AlertList,
  render: (args) => (
    <Grid
      sx={{
        position: 'absolute',
        right: 0,
        top: 0,
        width: '100%',
        justifyContent: 'flex-end',
        display: 'flex',
      }}
    >
      <AlertList {...args} />
    </Grid>
  ),
};

export default meta;
type Story = StoryObj<typeof AlertList>;

export const Default: Story = {
  args: {
    vitalsAlerts: [
      {
        type: ALERT_TYPES.VITALS,
        id: 'A-001',
        code: VITALS_ALERT_CODES.HR_LOW_AUDIO.code,
        deviceCode: SENSOR_CODES.chest,
        priority: ALERT_PRIORITY.MEDIUM,
        acknowledged: false,
        timestamp: '2023-01-01 12:00:00.0000',
      },
      {
        type: ALERT_TYPES.VITALS,
        id: 'A-002',
        code: VITALS_ALERT_CODES.RR_HIGH_AUDIO.code,
        deviceCode: SENSOR_CODES.chest,
        priority: ALERT_PRIORITY.MEDIUM,
        acknowledged: false,
        timestamp: '2023-01-01 12:00:15.0000',
      },
    ],
    deviceAlerts: [],
  },
};
