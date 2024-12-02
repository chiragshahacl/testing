import BedCard from '@/components/cards/BedCard';
import { PatientsData } from '@/context/PatientsContext';
import { EncounterStatus } from '@/types/encounters';
import { SENSOR_TYPES } from '@/types/sensor';
import {
  ALERT_PRIORITY,
  ALERT_TYPES,
  DEVICE_ALERT_CODES,
  VITALS_ALERT_CODES,
} from '@/utils/metricCodes';
import { action } from '@storybook/addon-actions';
import { jest } from '@storybook/jest';
import { Meta, StoryObj } from '@storybook/react';

const meta: Meta<typeof BedCard> = {
  component: BedCard,
  decorators: [
    (Story, context) => (
      <PatientsData.Provider
        value={{
          selectedBed: {
            id: 'B-001',
            bedNo: 'B-001',
          },
          updateSelectedBed: action('onUpdateSelectedBed'),
          loadingSelectedBed: false,
          getGroupById: jest.fn(),
          getActiveGroup: jest.fn(),
          updateActiveGroup: jest.fn(),
          activeGroupId: '',
          setBedManagementModal: jest.fn(),
          bedManagementModalIsOpen: false,
          resetPatientsContext: jest.fn(),
          bedsDisplayGroups: [],
          updateBedsOnDisplay: jest.fn(),
          bedsDisplayGroupsKeepAlive: jest.fn(),
          removeSelfFromBedsDisplayGroup: jest.fn(),
          groupManagementModalIsOpen: false,
          setGroupManagementModal: jest.fn(),
          monitorsFreshDataKeepAlive: {
            current: {},
          },
          resetMonitorsKeepAlive: jest.fn(),
          updateKeepAlive: jest.fn(),
          ...context.args,
        }}
      >
        <Story />
      </PatientsData.Provider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof BedCard>;

export const Default: Story = {
  args: {
    title: 'Bed ID 008',
    bedId: '008',
    metrics: {
      hr: {
        value: 100,
        unit: 'bpm',
        timestamp: '1697078057916',
      },
      spo2: {
        value: 80,
        unit: '',
        timestamp: '1697078057916',
      },
    },
    alertThresholds: {
      '258418': {
        upperLimit: '120',
        lowerLimit: '45',
      },
      '258420': {
        upperLimit: '100',
        lowerLimit: '85',
      },
    },
    alerts: [],
    activeSensors: [
      {
        id: 'SEN-EM-001',
        title: 'Chest Sensor',
        primaryIdentifier: 'chest_sensor_001',
        type: SENSOR_TYPES.CHEST,
        patientMonitorId: 'PM-001',
      },
      {
        id: 'SEN-EM-002',
        title: 'Limb Sensor',
        primaryIdentifier: 'limb_sensor_001',
        type: SENSOR_TYPES.LIMB,
        patientMonitorId: 'PM-002',
      },
    ],
  },
};

export const BedCardWithHrAlerts: Story = {
  args: {
    title: 'Bed ID 008',
    bedId: '008',
    metrics: {
      hr: {
        value: 100,
        unit: 'bpm',
        timestamp: '1697078057916',
      },
      spo2: {
        value: 80,
        unit: '',
        timestamp: '1697078057916',
      },
    },
    alertThresholds: {
      '258418': {
        upperLimit: '120',
        lowerLimit: '45',
      },
      '258420': {
        upperLimit: '100',
        lowerLimit: '85',
      },
    },
    alerts: [
      {
        type: ALERT_TYPES.VITALS,
        id: 'A-002',
        code: VITALS_ALERT_CODES.HR_HIGH_AUDIO.code,
        deviceCode: 'ANNE Chest',
        priority: ALERT_PRIORITY.HIGH,
        acknowledged: false,
        timestamp: '001',
      },
    ],
    activeSensors: [
      {
        id: 'SEN-EM-001',
        title: 'Chest Sensor',
        primaryIdentifier: 'chest_sensor_001',
        type: SENSOR_TYPES.CHEST,
        patientMonitorId: 'PM-001',
      },
      {
        id: 'SEN-EM-002',
        title: 'Limb Sensor',
        primaryIdentifier: 'limb_sensor_001',
        type: SENSOR_TYPES.LIMB,
        patientMonitorId: 'PM-002',
      },
    ],
  },
};

export const BedCardWithSpoAlerts: Story = {
  args: {
    title: 'Bed ID 008',
    bedId: '008',
    metrics: {
      hr: {
        value: 100,
        unit: 'bpm',
        timestamp: '1697078057916',
      },
      spo2: {
        value: 80,
        unit: '',
        timestamp: '1697078057916',
      },
    },
    alertThresholds: {
      '258418': {
        upperLimit: '120',
        lowerLimit: '45',
      },
      '258420': {
        upperLimit: '100',
        lowerLimit: '85',
      },
    },
    alerts: [
      {
        type: ALERT_TYPES.VITALS,
        id: 'A-002',
        code: VITALS_ALERT_CODES.SPO2_HIGH_AUDIO.code,
        deviceCode: 'ANNE Chest',
        priority: ALERT_PRIORITY.HIGH,
        acknowledged: false,
        timestamp: '001',
      },
    ],
    activeSensors: [
      {
        id: 'SEN-EM-001',
        title: 'Chest Sensor',
        primaryIdentifier: 'chest_sensor_001',
        type: SENSOR_TYPES.CHEST,
        patientMonitorId: 'PM-001',
      },
      {
        id: 'SEN-EM-002',
        title: 'Limb Sensor',
        primaryIdentifier: 'limb_sensor_001',
        type: SENSOR_TYPES.LIMB,
        patientMonitorId: 'PM-002',
      },
    ],
    encounterStatus: EncounterStatus.IN_PROGRESS,
  },
};

export const BedCardWithTechnicalAlerts: Story = {
  args: {
    title: 'Bed ID 008',
    bedId: '008',
    metrics: {
      hr: {
        value: 100,
        unit: 'bpm',
        timestamp: '1697078057916',
      },
      spo2: {
        value: 80,
        unit: '',
        timestamp: '1697078057916',
      },
    },
    alertThresholds: {
      '258418': {
        upperLimit: '120',
        lowerLimit: '45',
      },
      '258420': {
        upperLimit: '100',
        lowerLimit: '85',
      },
    },
    alerts: [
      {
        type: ALERT_TYPES.DEVICE,
        id: 'A-001',
        code: DEVICE_ALERT_CODES.OUT_OF_RANGE_ALERT.code,
        deviceCode: 'ANNE Chest',
        priority: ALERT_PRIORITY.LOW,
        acknowledged: false,
        timestamp: '000',
      },
    ],
    activeSensors: [
      {
        id: 'SEN-EM-001',
        title: 'Chest Sensor',
        primaryIdentifier: 'chest_sensor_001',
        type: SENSOR_TYPES.CHEST,
        patientMonitorId: 'PM-001',
      },
      {
        id: 'SEN-EM-002',
        title: 'Limb Sensor',
        primaryIdentifier: 'limb_sensor_001',
        type: SENSOR_TYPES.LIMB,
        patientMonitorId: 'PM-002',
      },
    ],
  },
};

export const BedCardWithoutAssociatedMonitor: Story = {
  args: {
    title: 'Bed ID 008',
    bedId: '008',
    metrics: {},
    alertThresholds: {},
    alerts: [],
    activeSensors: [],
    hasAssociatedMonitor: false,
  },
};

export const BedCardWithoutPatientSession: Story = {
  args: {
    title: 'Bed ID 008',
    bedId: '008',
    metrics: {},
    alertThresholds: {},
    alerts: [],
    activeSensors: [],
  },
};

export const BedCardWithPatientMonitorAlerts: Story = {
  args: {
    title: 'Bed ID 008',
    bedId: '008',
    metrics: {
      hr: {
        value: 100,
        unit: 'bpm',
        timestamp: '1697078057916',
      },
      spo2: {
        value: 80,
        unit: '',
        timestamp: '1697078057916',
      },
    },
    alertThresholds: {
      '258418': {
        upperLimit: '120',
        lowerLimit: '45',
      },
      '258420': {
        upperLimit: '100',
        lowerLimit: '85',
      },
    },
    alerts: [
      {
        type: ALERT_TYPES.DEVICE,
        id: 'A-001',
        code: DEVICE_ALERT_CODES.MONITOR_NOT_AVAILABLE_ALERT.code,
        deviceCode: 'monitor',
        priority: ALERT_PRIORITY.HIGH,
        acknowledged: false,
        timestamp: '000',
      },
    ],
    activeSensors: [
      {
        id: 'SEN-EM-001',
        title: 'Chest Sensor',
        primaryIdentifier: 'chest_sensor_001',
        type: SENSOR_TYPES.CHEST,
        patientMonitorId: 'PM-001',
      },
      {
        id: 'SEN-EM-002',
        title: 'Limb Sensor',
        primaryIdentifier: 'limb_sensor_001',
        type: SENSOR_TYPES.LIMB,
        patientMonitorId: 'PM-002',
      },
    ],
    encounterStatus: EncounterStatus.IN_PROGRESS,
  },
};

export const SelectedBedCardWithoutPatient: Story = {
  args: {
    title: 'Bed ID 008',
    bedId: '008',
    metrics: {
      hr: {
        value: 100,
        unit: 'bpm',
        timestamp: '1697078057916',
      },
      spo2: {
        value: 80,
        unit: '',
        timestamp: '1697078057916',
      },
    },
    alertThresholds: {
      '258418': {
        upperLimit: '120',
        lowerLimit: '45',
      },
      '258420': {
        upperLimit: '100',
        lowerLimit: '85',
      },
    },
    alerts: [],
    activeSensors: [
      {
        id: 'SEN-EM-001',
        title: 'Chest Sensor',
        primaryIdentifier: 'chest_sensor_001',
        type: SENSOR_TYPES.CHEST,
        patientMonitorId: 'PM-001',
      },
      {
        id: 'SEN-EM-002',
        title: 'Limb Sensor',
        primaryIdentifier: 'limb_sensor_001',
        type: SENSOR_TYPES.LIMB,
        patientMonitorId: 'PM-002',
      },
    ],
  },
};

export const SelectedBedCard: Story = {
  args: {
    title: 'Bed ID 008',
    bedId: '008',
    metrics: {
      hr: {
        value: 100,
        unit: 'bpm',
        timestamp: '1697078057916',
      },
      spo2: {
        value: 80,
        unit: '',
        timestamp: '1697078057916',
      },
    },
    alertThresholds: {
      '258418': {
        upperLimit: '120',
        lowerLimit: '45',
      },
      '258420': {
        upperLimit: '100',
        lowerLimit: '85',
      },
    },
    alerts: [],
    activeSensors: [
      {
        id: 'SEN-EM-001',
        title: 'Chest Sensor',
        primaryIdentifier: 'chest_sensor_001',
        type: SENSOR_TYPES.CHEST,
        patientMonitorId: 'PM-001',
      },
      {
        id: 'SEN-EM-002',
        title: 'Limb Sensor',
        primaryIdentifier: 'limb_sensor_001',
        type: SENSOR_TYPES.LIMB,
        patientMonitorId: 'PM-002',
      },
    ],
    encounterStatus: EncounterStatus.IN_PROGRESS,
  },
};
