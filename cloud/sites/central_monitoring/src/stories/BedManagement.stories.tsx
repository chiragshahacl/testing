import BedManagementModal from '@/components/modals/BedManagementModal';
import { faker } from '@faker-js/faker';
import { expect, jest } from '@storybook/jest';
import type { Meta, StoryObj } from '@storybook/react';
import { screen, userEvent, waitFor, within } from '@storybook/testing-library';
import { rest } from 'msw';
import { createServerSideBed } from './factories/ServerSideBedFactory';
import { createServerSidePatientMonitor } from './factories/ServerSidePatientMonitorFactory';
import { I18nextProvider } from 'react-i18next';
import { Suspense } from 'react';
import i18n from '@/app/i18n';

const multiple = faker.helpers.multiple;
const defaultPatientMonitors = multiple(createServerSidePatientMonitor, { count: 10 });
const defaultBeds = multiple(createServerSideBed, { count: 10 });

const onSaveBedChanges = jest.fn();
const onSaveAssignChanges = jest.fn();

const withI18next = (Story: any) => {
  return (
    // This catches the suspense from components not yet ready (still loading translations)
    // Alternative: set useSuspense to false on i18next.options.react when initializing i18next
    <Suspense fallback={<div>loading translations...</div>}>
      <I18nextProvider i18n={i18n}>
        <Story />
      </I18nextProvider>
    </Suspense>
  );
};

const meta: Meta<typeof BedManagementModal> = {
  component: BedManagementModal,
  args: {
    isOpen: true,
  },
  decorators: [
    withI18next,
    (Story) => {
      onSaveBedChanges.mockReset();
      onSaveAssignChanges.mockReset();
      return <Story />;
    },
  ],
};

export default meta;
type Story = StoryObj<typeof BedManagementModal>;

export const Default: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.get('/web/device', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultPatientMonitors,
            })
          );
        }),
        rest.get('/web/bed', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultBeds,
            })
          );
        }),
      ],
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await waitFor(async () => {
      const AssignBedsTitle = canvas.getByTestId('assign-beds-title');
      const FinishSetupButton = canvas.getByTestId('finish-bed-setup');

      await expect(AssignBedsTitle).toBeInTheDocument();
      await expect(FinishSetupButton).toBeInTheDocument();
      await expect(FinishSetupButton).not.toBeEnabled();
    });
  },
};

export const DefaultFirstStep: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.get('/web/device', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: [],
            })
          );
        }),
        rest.get('/web/bed', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: [],
            })
          );
        }),
      ],
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await waitFor(async () => {
      const NoBedsText = canvas.getByTestId('no-beds-text');
      await expect(NoBedsText).toBeInTheDocument();
      const AddBedsTitle = canvas.getByTestId('add-beds-title');
      await expect(AddBedsTitle).toBeInTheDocument();
      await expect(AddBedsTitle).toHaveTextContent('(0)');

      const NextButton = canvas.getByTestId('next-assign-beds');
      await expect(NextButton).toBeInTheDocument();
      await expect(NextButton).toBeDisabled();
    });
  },
};

export const AddNewBed: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.get('/web/device', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: [],
            })
          );
        }),
        rest.get('/web/bed', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: [],
            })
          );
        }),
      ],
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await waitFor(async () => {
      const AddBedButton = canvas.getByTestId('add-bed');
      await expect(AddBedButton).toBeInTheDocument();
      await expect(AddBedButton).toBeEnabled();
      await userEvent.click(AddBedButton);

      const AddBedsTitle = canvas.getByTestId('add-beds-title');
      await expect(AddBedsTitle).toBeInTheDocument();
      await expect(AddBedsTitle).toHaveTextContent('(1)');

      const NewBedField = canvas.getByRole('textbox');
      await expect(NewBedField).toBeInTheDocument();
      await userEvent.keyboard('001');
      await expect(NewBedField).toHaveValue('001');
    });
  },
};

export const RemoveBed: Story = {
  args: {
    initialStep: 1,
  },
  parameters: {
    msw: {
      handlers: [
        rest.get('/web/device', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultPatientMonitors,
            })
          );
        }),
        rest.get('/web/bed', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultBeds,
            })
          );
        }),
      ],
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await waitFor(async () => {
      const AddBedsTitle = canvas.getByTestId('add-beds-title');
      await expect(AddBedsTitle).toBeInTheDocument();
      await expect(AddBedsTitle).toHaveTextContent('(10)');

      const RemoveBedButton = canvas.getByTestId('remove-bed-1');
      await expect(RemoveBedButton).toBeInTheDocument();
      await expect(RemoveBedButton).toBeEnabled();
      await userEvent.click(RemoveBedButton);

      await expect(RemoveBedButton).not.toBeInTheDocument();
      await expect(AddBedsTitle).toHaveTextContent('(9)');
    });
  },
};

export const AssignBedMonitor: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.get('/web/device', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultPatientMonitors,
            })
          );
        }),
        rest.get('/web/bed', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultBeds,
            })
          );
        }),
        rest.put('/web/device/bed/batch', (_, res, ctx) => {
          onSaveAssignChanges();
          return res(ctx.status(204));
        }),
      ],
    },
  },
  play: async ({ canvasElement, args: { onClose } }) => {
    const canvas = within(canvasElement);
    await waitFor(async () => {
      const AssignBedsTitle = canvas.getByTestId('assign-beds-title');
      const FinishSetupButton = canvas.getByTestId('finish-bed-setup');

      await expect(AssignBedsTitle).toBeInTheDocument();
      await expect(FinishSetupButton).toBeInTheDocument();
      await expect(FinishSetupButton).not.toBeEnabled();

      const FirstMonitorBed = (await canvas.findAllByRole('combobox'))[0];
      await expect(FirstMonitorBed).toBeInTheDocument();
      await userEvent.click(FirstMonitorBed, { pointerEventsCheck: 0 }); // Bypasses pointer-events: none
    });
    await waitFor(async () => {
      const FinishSetupButton = canvas.getByTestId('finish-bed-setup');
      const FirstBedOption = screen.getByTestId('select-option-0');
      await userEvent.click(FirstBedOption);

      await expect(FinishSetupButton).toBeEnabled();
      await userEvent.click(FinishSetupButton);
    });
    await waitFor(async () => {
      const FinishAssignmentModal = screen.getByTestId('finish-assignment-confirmation');
      await expect(FinishAssignmentModal).toBeInTheDocument();

      const ConfirmButton = screen.getByTestId('confirm');
      await expect(ConfirmButton).toBeInTheDocument();
      await expect(ConfirmButton).toBeEnabled();

      await userEvent.click(ConfirmButton);
    });
    await waitFor(async () => {
      await expect(onSaveAssignChanges).toHaveBeenCalled();
      await expect(onClose).toHaveBeenCalled();
    });
  },
};

/*
 * Requirement IDs: RQ-00022-B: SR-1.2.3.11 RQ-00022-B: SR-1.2.2.8
 */
export const MoveBetweenSteps: Story = {
  args: {
    initialStep: 1,
  },
  parameters: {
    msw: {
      handlers: [
        rest.get('/web/device', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultPatientMonitors,
            })
          );
        }),
        rest.get('/web/bed', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultBeds,
            })
          );
        }),
        rest.put('/web/bed/batch', (_, res, ctx) => {
          onSaveBedChanges();
          return res(ctx.status(204));
        }),
      ],
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await waitFor(async () => {
      const AddBedsTitle = canvas.getByTestId('add-beds-title');
      await expect(AddBedsTitle).toBeInTheDocument();

      const NextButton = canvas.getByTestId('next-assign-beds');
      await expect(NextButton).toBeInTheDocument();
      await expect(NextButton).toBeEnabled();
      await userEvent.click(NextButton);
      await expect(AddBedsTitle).not.toBeInTheDocument();
      await expect(NextButton).not.toBeInTheDocument();
    });
    await waitFor(async () => {
      await expect(onSaveBedChanges).toHaveBeenCalled();
      const AssignBedsTitle = canvas.getByTestId('assign-beds-title');
      await expect(AssignBedsTitle).toBeInTheDocument();

      const BackButton = canvas.getByTestId('back-add-beds');
      await expect(BackButton).toBeInTheDocument();
      await expect(BackButton).toBeEnabled();
      await userEvent.click(BackButton);

      const AddBedsTitle = canvas.getByTestId('add-beds-title');
      const NextButton = canvas.getByTestId('next-assign-beds');
      await expect(AssignBedsTitle).not.toBeInTheDocument();
      await expect(BackButton).not.toBeInTheDocument();
      await expect(AddBedsTitle).toBeInTheDocument();
      await expect(NextButton).toBeInTheDocument();
    });
  },
};

/*
 * Requirement IDs: RQ-00022-B: SR-1.2.3.22
 */
export const FetchErrorFirstStep: Story = {
  args: {
    initialStep: 1,
  },
  parameters: {
    msw: {
      handlers: [
        rest.get('/web/device', (_, res, ctx) => {
          return res(ctx.status(500));
        }),
        rest.get('/web/bed', (_, res, ctx) => {
          return res(ctx.status(500));
        }),
      ],
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await waitFor(async () => {
      const AddBedsError = canvas.getByTestId('add-beds-error');

      await expect(AddBedsError).toBeInTheDocument();
    });
  },
};

/*
 * Requirement IDs: 	RQ-00022-B: SR-1.2.3.24
 */
export const FetchErrorSecondStep: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.get('/web/device', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultPatientMonitors,
            })
          );
        }),
        rest.get('/web/bed', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultBeds,
            })
          );
        }),
      ],
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await waitFor(async () => {
      const AssignBedsError = canvas.getByTestId('assign-beds-error');

      await expect(AssignBedsError).toBeInTheDocument();
    });
  },
};

/*
 * Requirement IDs: RQ-00022-B: SR-1.2.3.23
 */
export const AssignBedsError: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.get('/web/device', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: multiple(createServerSidePatientMonitor, { count: 1 }),
            })
          );
        }),
        rest.get('/web/bed', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultBeds,
            })
          );
        }),
        rest.put('/web/device/bed/batch', (_, res, ctx) => {
          return res(ctx.status(500));
        }),
      ],
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await waitFor(async () => {
      const FirstMonitorBed = (await canvas.findAllByRole('combobox'))[0];
      await expect(FirstMonitorBed).toBeInTheDocument();
      await userEvent.click(FirstMonitorBed, { pointerEventsCheck: 0 }); // Bypasses pointer-events: none
    });
    await waitFor(async () => {
      const FinishSetupButton = canvas.getByTestId('finish-bed-setup');
      const FirstBedOption = screen.getByTestId('select-option-0');
      await userEvent.click(FirstBedOption);

      await expect(FinishSetupButton).toBeEnabled();
      await userEvent.click(FinishSetupButton);
    });
    await waitFor(async () => {
      const ErrorModal = screen.getByTestId('modify-server-error');
      await expect(ErrorModal).toBeInTheDocument();
    });
  },
};

/*
 * Requirement IDs: RQ-00022-B: SR-1.2.2.16  RQ-00022-B: SR-1.2.2.16
 */
export const SaveBedsError: Story = {
  args: {
    initialStep: 1,
  },
  parameters: {
    msw: {
      handlers: [
        rest.get('/web/device', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultPatientMonitors,
            })
          );
        }),
        rest.get('/web/bed', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultBeds,
            })
          );
        }),
        rest.put('/web/bed/batch', (_, res, ctx) => {
          return res(ctx.status(500));
        }),
      ],
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await waitFor(() => {
      expect(canvas.getByTestId('add-beds-title')).toHaveTextContent('(10)');
    });
    const AssignButton = canvas.getByTestId('next-assign-beds');
    expect(AssignButton).toBeEnabled();
    await userEvent.click(AssignButton);

    await waitFor(() => {
      expect(screen.getByTestId('modify-server-error')).toBeInTheDocument();
    });
  },
};
