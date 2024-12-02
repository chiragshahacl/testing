import IntegratingWithEHR from '@/app/technical/home/IntegratingWithEHR';
import { Meta, StoryObj } from '@storybook/react';
import { expect, jest } from '@storybook/jest';
import { userEvent, screen, waitFor } from '@storybook/testing-library';
import { rest } from 'msw';

const meta: Meta<typeof IntegratingWithEHR> = {
  title: 'Technical/Components/IntegratingWithEHR',
  component: IntegratingWithEHR,
  parameters: {
    msw: {
      handlers: [
        rest.put('/web/config', (req, res, ctx) => {
          return res(ctx.status(200));
        }),
      ],
    },
  },
};

export default meta;
type Story = StoryObj<typeof IntegratingWithEHR>;

export const Default: Story = {
  args: {
    values: {
      host: 'example.com',
      port: 1234,
      interval: 5,
    },
    showIntegrationSuccess: jest.fn(),
    onSave: jest.fn(),
    onCancelSave: jest.fn(),
    validPassword: 'password',
  },
};

const setSubmitDisabled = jest.fn();
const setProcessingForm = jest.fn();

export const Cancel: Story = {
  args: {
    values: {
      host: 'example.com',
      port: 1234,
      interval: 5,
    },
    showIntegrationSuccess: jest.fn(),
    onSave: jest.fn(),
    onCancelSave: jest.fn(),
    validPassword: 'password',
  },
  play: async () => {
    const CancelButton = screen.getByTestId('cancel-button');

    expect(CancelButton).toBeEnabled();
    await userEvent.click(CancelButton);
    await waitFor(() => {
      expect(CancelButton).toBeDisabled();
    });
  },
};
