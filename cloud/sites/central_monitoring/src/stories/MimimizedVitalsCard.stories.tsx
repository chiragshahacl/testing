import MinimizedVitalsCard from '@/components/cards/MinimizedVitalsCard';
import { Meta, StoryObj } from '@storybook/react';

const meta: Meta<typeof MinimizedVitalsCard> = {
  component: MinimizedVitalsCard,
};

export default meta;
type Story = StoryObj<typeof MinimizedVitalsCard>;

export const Default: Story = {
  args: {
    isLoading: false,
    isPatientMonitorAvailable: true,
    technicalAlerts: {
      HR: false,
      SPO: false,
      RR_METRIC: false,
      BODY_TEMP: false,
      CHEST_TEMP: false,
      FALLS: false,
      BODY_POSITION: false,
      PI: false,
      PR: false,
      LIMB_TEMP: false,
      PULSE: false,
      NIBP: false,
    },
    metricInfo: {
      HR: {
        limits: {
          upperLimit: 120,
          lowerLimit: 45,
        },
        value: 80,
        isSensorConnected: true,
        hasAlert: true,
      },
      SPO: {
        limits: {
          upperLimit: 100,
          lowerLimit: 85,
        },
        value: 90,
        isSensorConnected: true,
        hasAlert: false,
      },
    },
  },
};
