import type { Meta, StoryObj } from '@storybook/react';

import NetworkStatusModal from '@/components/modals/NetworkStatusModal';

const meta: Meta<typeof NetworkStatusModal> = {
  component: NetworkStatusModal,
};

export default meta;
type Story = StoryObj<typeof NetworkStatusModal>;

export const Default: Story = {
  args: {
    isOnline: false,
    title: 'Network error',
    description: 'some desc',
  },
};
