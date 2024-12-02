import { expect, jest } from '@storybook/jest';
import { Meta, StoryObj } from '@storybook/react';
import { userEvent, waitFor, within } from '@storybook/testing-library';
import { rest } from 'msw';
import TabPanel from '../app/(authenticated)/home/details/Tabs/TabPanel';
import { MockBeds } from '@/utils/groupsMockData';

const meta: Meta<typeof TabPanel> = {
  component: TabPanel,
  title: 'Single Patient/Tabs',
  args: {
    metrics: {},
    selectedBed: MockBeds[0],
    selectedBedGraphsWithData: [],
    selectedTab: '',
    activeSensors: [],
    isLoading: false,
    alertThresholds: {},
    onTabSelected: jest.fn(),
    sendNewDataSeries: jest.fn(),
    deviceAlerts: [],
    vitalsAlerts: [],
    hasActivePatientSession: true,
  },
};

export default meta;
type Story = StoryObj<typeof TabPanel>;

export const Default: Story = {};

export const VitalsSelected: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    expect(canvas.getByTestId('vitals-tab')).toBeInTheDocument();
    expect(canvas.queryByTestId('alarm-limits-tab')).not.toBeInTheDocument();
    expect(canvas.queryByTestId('patient-info-tab')).not.toBeInTheDocument();
    expect(canvas.queryByTestId('alarm-history-tab')).not.toBeInTheDocument();
  },
};

export const AlarmLimitsSelected: Story = {
  args: {
    selectedTab: 'vital_management',
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    expect(canvas.queryByTestId('vitals-tab')).not.toBeInTheDocument();
    expect(canvas.getByTestId('alarm-limits-tab')).toBeInTheDocument();
    expect(canvas.queryByTestId('patient-info-tab')).not.toBeInTheDocument();
    expect(canvas.queryByTestId('alarm-history-tab')).not.toBeInTheDocument();
  },
};

export const PatientInfoSelected: Story = {
  args: {
    selectedTab: 'patient_info',
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    expect(canvas.queryByTestId('vitals-tab')).not.toBeInTheDocument();
    expect(canvas.queryByTestId('alarm-limits-tab')).not.toBeInTheDocument();
    expect(canvas.getByTestId('patient-info-tab')).toBeInTheDocument();
    expect(canvas.queryByTestId('alarm-history-tab')).not.toBeInTheDocument();
  },
};

export const AlarmHistorySelected: Story = {
  args: {
    selectedTab: 'alarm_history',
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    expect(canvas.queryByTestId('vitals-tab')).not.toBeInTheDocument();
    expect(canvas.queryByTestId('alarm-limits-tab')).not.toBeInTheDocument();
    expect(canvas.queryByTestId('patient-info-tab')).not.toBeInTheDocument();
    expect(canvas.getByTestId('alarm-history-tab')).toBeInTheDocument();
  },
};
