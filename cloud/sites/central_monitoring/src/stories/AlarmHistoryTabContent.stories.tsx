import { expect, jest } from '@storybook/jest';
import { Meta, StoryObj } from '@storybook/react';
import { generateDataArray } from './factories/AlarmHistoryFactory';
import { ALERT_PRIORITY } from '@/utils/metricCodes';
import AlarmHistoryTabContent from '@/app/(authenticated)/home/details/Tabs/AlarmHistoryTabContent';

const meta: Meta<typeof AlarmHistoryTabContent> = {
  component: AlarmHistoryTabContent,
  title: 'Single Patient/Tabs/Alarm History',
  args: {
    alarmHistory: generateDataArray(5),
  },
  decorators: [
    (Story) => (
      <div style={{ width: '90vw' }}>
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof AlarmHistoryTabContent>;

export const Default: Story = {};

export const LargeRecord: Story = {
  args: {
    alarmHistory: generateDataArray(100),
  },
};

export const NoRecords: Story = {
  args: {
    alarmHistory: [],
  },
};

export const LongAlarmMessage: Story = {
  args: {
    alarmHistory: [
      {
        type: 'Physiological',
        date: 'Wed Jun 12 2024 15:00:00 GMT+0000',
        time: 'Wed Jun 12 2024 15:00:00 GMT+0000',
        priority: ALERT_PRIORITY.HIGH,
        message: 'This is an unexpectedly long message for alarm recorded',
        duration: '2573',
      },
    ],
  },
};

export const InvalidData: Story = {
  args: {
    alarmHistory: [
      {
        type: 'Physiological',
        date: 'Wed Jun 12 2024 15:00:00 GMT+0000',
        time: 'Wed Jun 12 2024 15:00:00 GMT+0000',
        priority: ALERT_PRIORITY.HIGH,
        message: '',
        duration: '2573',
      },
      {
        type: '',
        date: 'Wed Jun 12 2024 15:00:00 GMT+0000',
        time: 'Wed Jun 12 2024 15:00:00 GMT+0000',
        priority: ALERT_PRIORITY.MEDIUM,
        message: 'Message',
        duration: '2573',
      },
      {
        type: 'Physiological',
        date: '',
        time: 'Wed Jun 12 2024 15:00:00 GMT+0000',
        priority: ALERT_PRIORITY.LOW,
        message: 'Message',
        duration: '2573',
      },
      {
        type: 'Physiological',
        date: 'Wed Jun 12 2024 15:00:00 GMT+0000',
        time: '',
        priority: ALERT_PRIORITY.HIGH,
        message: 'Message',
        duration: '2573',
      },
      {
        type: 'Physiological',
        date: 'Wed Jun 12 2024 15:00:00 GMT+0000',
        time: 'Wed Jun 12 2024 15:00:00 GMT+0000',
        priority: ALERT_PRIORITY.INTERNAL,
        message: 'Message',
        duration: '2573',
      },
      {
        type: 'Physiological',
        date: 'Wed Jun 12 2024 15:00:00 GMT+0000',
        time: 'Wed Jun 12 2024 15:00:00 GMT+0000',
        priority: ALERT_PRIORITY.HIGH,
        message: 'Message',
        duration: '',
      },
    ],
  },
};
