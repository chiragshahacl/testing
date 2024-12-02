import GroupManagementModal from '@/components/modals/GroupManagementModal';
import { bedManagementErrors, groupManagementErrors } from '@/constants';
import { faker } from '@faker-js/faker';
import { expect, jest } from '@storybook/jest';
import type { Meta, StoryObj } from '@storybook/react';
import { screen, userEvent, waitFor } from '@storybook/testing-library';
import { rest } from 'msw';
import { createServerSideBed } from './factories/ServerSideBedFactory';
import { createServerSideGroup } from './factories/ServerSideGroupFactory';
import { createServerSidePatientMonitor } from './factories/ServerSidePatientMonitorFactory';

const multiple = faker.helpers.multiple;
const onSaveBedChanges = jest.fn();
const onSaveGroupChanges = jest.fn();

const meta: Meta<typeof GroupManagementModal> = {
  component: GroupManagementModal,
  args: {
    isOpen: true,
  },
  decorators: [
    (Story) => {
      onSaveBedChanges.mockReset();
      onSaveGroupChanges.mockReset();
      return <Story />;
    },
  ],
};

const defaultServerSideBeds = multiple(createServerSideBed, { count: 10 });
const defaultServerSideGroups = multiple(
  () => createServerSideGroup({ beds: defaultServerSideBeds.slice(0, 5), name: 'Group 1' }),
  {
    count: 1,
  }
);
const defaultServerSideMonitors = multiple(createServerSidePatientMonitor, {
  count: 1,
});

export default meta;
type Story = StoryObj<typeof GroupManagementModal>;

export const Default: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.get('/web/bed', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultServerSideBeds,
            })
          );
        }),
        rest.get('/web/bed-group', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultServerSideGroups,
            })
          );
        }),
        rest.get('/web/device', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultServerSideMonitors,
            })
          );
        }),
      ],
    },
  },
};

export const NoData: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.get('/web/bed', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultServerSideBeds,
            })
          );
        }),
        rest.get('/web/bed-group', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: [],
            })
          );
        }),
        rest.get('/web/device', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultServerSideMonitors,
            })
          );
        }),
      ],
    },
  },
};

export const AddNewGroup: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.get('/web/bed', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: [],
            })
          );
        }),
        rest.get('/web/bed-group', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: [],
            })
          );
        }),
        rest.get('/web/device', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: [],
            })
          );
        }),
      ],
    },
  },
  play: async () => {
    await waitFor(async () => {
      expect(screen.getByTestId('add-group')).toBeInTheDocument();
    });
    const addGroupButton = screen.getByTestId('add-group');
    expect(addGroupButton).toBeEnabled();

    await userEvent.click(addGroupButton, { pointerEventsCheck: 0 }); // Bypasses pointer-events: none

    await waitFor(async () => {
      expect(screen.getByDisplayValue('Group 1')).toBeInTheDocument();
    });

    const finishSetupButton = screen.getByTestId('finish-setup-button');
    expect(finishSetupButton).toBeInTheDocument();
    expect(finishSetupButton).toBeDisabled();

    await userEvent.keyboard('2');
    expect(screen.getByDisplayValue('Group 12')).toBeInTheDocument();
  },
};

export const UpdateGroupName: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.get('/web/bed', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultServerSideBeds,
            })
          );
        }),
        rest.get('/web/bed-group', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultServerSideGroups,
            })
          );
        }),
        rest.get('/web/device', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultServerSideMonitors,
            })
          );
        }),
      ],
    },
  },
  play: async () => {
    await waitFor(async () => {
      expect(screen.getByDisplayValue('Group 1')).toBeInTheDocument();
    });
    const editButton = screen.getByTestId('edit-group-name');
    await expect(editButton).toBeInTheDocument();
    await userEvent.click(editButton);

    await userEvent.keyboard('2');
    expect(screen.getByDisplayValue('Group 12')).toBeInTheDocument();

    // Confirm it no longer allows edit after clicking somewhere else
    const managementModal = screen.getByTestId('Group Management-modal');
    await userEvent.click(managementModal);
    await userEvent.keyboard('3');
    await waitFor(async () => {
      expect(screen.queryByDisplayValue('Group 123')).not.toBeInTheDocument();
    });
  },
};

/*
 * Requirement IDs: RQ-00022-B: SR-1.2.4.1, SR-1.2.4.5, SR-1.2.4.6, SR-1.2.4.34
 */
export const AddNewBed: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.get('/web/bed', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultServerSideBeds,
            })
          );
        }),
        rest.get('/web/bed-group', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: [
                {
                  id: faker.string.uuid(),
                  name: faker.lorem.slug(),
                  beds: [],
                },
              ],
            })
          );
        }),
        rest.get('/web/device', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultServerSideMonitors,
            })
          );
        }),
      ],
    },
  },
  play: async () => {
    await waitFor(() => {
      expect(screen.getAllByRole('checkbox')).toHaveLength(10);
    });
    const finishSetupButton = screen.getByTestId('finish-setup-button');
    const totalBeds = screen.getByTestId('total-beds');

    expect(finishSetupButton).toBeDisabled();
    expect(totalBeds).toHaveTextContent('0 total');

    const addBedButton = screen.getAllByRole('checkbox')[0];
    await expect(addBedButton).toBeInTheDocument();
    await expect(addBedButton).toBeEnabled();
    await userEvent.click(addBedButton);

    await expect(finishSetupButton).toBeEnabled();
    await expect(totalBeds).toHaveTextContent('1 total');
  },
};

export const SavesNewChanges: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.get('/web/bed', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultServerSideBeds,
            })
          );
        }),
        rest.get('/web/bed-group', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: [
                {
                  id: faker.string.uuid(),
                  name: faker.lorem.slug(),
                  beds: [],
                },
              ],
            })
          );
        }),
        rest.get('/web/device', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultServerSideMonitors,
            })
          );
        }),
        rest.put('/web/bed-group/batch', (_, res, ctx) => {
          onSaveGroupChanges();
          return res(ctx.status(204));
        }),
        rest.put('/web/bed-group/beds/batch', (_, res, ctx) => {
          onSaveBedChanges();
          return res(ctx.status(204));
        }),
      ],
    },
  },
  play: async ({ args: { onClose } }) => {
    await waitFor(() => {
      expect(screen.getAllByRole('checkbox')).toHaveLength(10);
    });
    const addBedButton = screen.getAllByRole('checkbox')[0];
    expect(addBedButton).toBeInTheDocument();
    expect(addBedButton).toBeEnabled();
    await userEvent.click(addBedButton);

    const finishSetupButton = screen.getByTestId('finish-setup-button');
    expect(finishSetupButton).toBeEnabled();
    await userEvent.click(finishSetupButton);

    const confirmationModal = screen.getByTestId('finish-setup-confirmation');
    expect(confirmationModal).toBeInTheDocument();
    const confirmButton = screen.getByTestId('Confirm');
    await userEvent.click(confirmButton);
    await waitFor(() => {
      expect(onSaveGroupChanges).toBeCalled();
      expect(onSaveBedChanges).toBeCalled();
      expect(onClose).toBeCalled();
    });
  },
};

export const FetchErrors: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.get('/web/bed', (_, res, ctx) => {
          return res(ctx.status(500));
        }),
        rest.get('/web/bed-group', (_, res, ctx) => {
          return res(ctx.status(500));
        }),
      ],
    },
  },
  play: async () => {
    await waitFor(
      () => {
        const groupsErrorText = screen.getByText(groupManagementErrors['failedToFetch']);
        expect(groupsErrorText).toBeInTheDocument();

        const bedsErrorText = screen.getByText(bedManagementErrors['failedToFetch']);
        expect(bedsErrorText).toBeInTheDocument();
      },
      { timeout: 5000 }
    );
  },
};

/*
 * Requirement IDs: RQ-00022-B: SR-1.2.4.6 RQ-00022-B: SR-1.2.4.35
 */
export const DuplicatedGroupNameError: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.get('/web/bed', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultServerSideBeds,
            })
          );
        }),
        rest.get('/web/bed-group', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultServerSideGroups,
            })
          );
        }),
        rest.get('/web/device', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultServerSideMonitors,
            })
          );
        }),
      ],
    },
  },
  play: async () => {
    await waitFor(async () => {
      expect(screen.getByTestId('add-group')).toBeInTheDocument();
    });
    const addGroupButton = screen.getByTestId('add-group');
    expect(addGroupButton).toBeEnabled();

    await userEvent.click(addGroupButton, { pointerEventsCheck: 0 }); // Bypasses pointer-events: none
    await userEvent.keyboard('{backspace}1');

    const managementModal = screen.getByTestId('Group Management-modal');
    await userEvent.click(managementModal);

    const errorText = screen.getByText(groupManagementErrors['duplicateGroup']);
    expect(errorText).toBeInTheDocument();
  },
};

/*
 * Requirement IDs: RQ-00022-B: SR-1.2.4.7
 */
export const NoTwoEmptyGroupsError: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.get('/web/bed', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultServerSideBeds,
            })
          );
        }),
        rest.get('/web/bed-group', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultServerSideGroups,
            })
          );
        }),
        rest.get('/web/device', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultServerSideMonitors,
            })
          );
        }),
      ],
    },
  },
  play: async () => {
    await waitFor(async () => {
      expect(screen.getByTestId('add-group')).toBeInTheDocument();
    });
    const addGroupButton = screen.getByTestId('add-group');
    expect(addGroupButton).toBeEnabled();

    await userEvent.click(addGroupButton, { pointerEventsCheck: 0 });
    await userEvent.click(addGroupButton, { pointerEventsCheck: 0 });

    const errorText = screen.getByText(groupManagementErrors['emptyGroup']);
    expect(errorText).toBeInTheDocument();
  },
};

/*
 * Requirement IDs: RQ-00022-B: SR-1.2.4.43 	RQ-00022-B: SR-1.2.4.42
 */
export const SavesNewChangesError: Story = {
  parameters: {
    msw: {
      handlers: [
        rest.get('/web/bed', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultServerSideBeds,
            })
          );
        }),
        rest.get('/web/bed-group', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: [
                {
                  id: faker.string.uuid(),
                  name: faker.lorem.slug(),
                  beds: [],
                },
              ],
            })
          );
        }),
        rest.get('/web/device', (_, res, ctx) => {
          return res(
            ctx.json({
              resources: defaultServerSideMonitors,
            })
          );
        }),
        rest.put('/web/bed-group/batch', (_, res, ctx) => {
          onSaveGroupChanges();
          return res(ctx.status(500));
        }),
        rest.put('/web/bed-group/beds/batch', (_, res, ctx) => {
          onSaveBedChanges();
          return res(ctx.status(500));
        }),
      ],
    },
  },
  play: async () => {
    await waitFor(() => {
      expect(screen.getAllByRole('checkbox')).toHaveLength(10);
    });
    const addBedButton = screen.getAllByRole('checkbox')[0];
    expect(addBedButton).toBeInTheDocument();
    expect(addBedButton).toBeEnabled();
    await userEvent.click(addBedButton);

    const finishSetupButton = screen.getByTestId('finish-setup-button');
    expect(finishSetupButton).toBeEnabled();
    await userEvent.click(finishSetupButton);

    await waitFor(async () => {
      const confirmationModal = screen.getByTestId('finish-setup-confirmation');
      await expect(confirmationModal).toBeInTheDocument();
      const confirmButton = screen.getByTestId('Confirm');
      await userEvent.click(confirmButton);
    });

    await waitFor(async () => {
      const failureModal = screen.getByTestId('modify-server-error');
      await expect(failureModal).toBeInTheDocument();
    });
  },
};
