import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import * as managementApi from '@/api/managementApi';
import GroupManagementModal from '@/components/modals/GroupManagementModal';
import { PatientsData } from '@/context/PatientsContext';
import { MockBeds, MockGroups } from '@/utils/groupsMockData';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { cloneDeep } from 'lodash';

import { useBeds } from '@/api/useBeds';
import { useGroups } from '@/api/useGroups';
import { usePatientMonitors } from '@/api/usePatientMonitors';
import { AudioManager } from '@/context/AudioManagerContext';
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const mockUsePatientMonitors = usePatientMonitors;
jest.mock('@/api/usePatientMonitors');

const mockUseBeds = useBeds;
jest.mock('@/api/useBeds');

const mockUseGroups = useGroups;
jest.mock('@/api/useGroups');

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 0,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
    },
  },
});

jest.mock('../src/utils/runtime', () => ({
  getCachedRuntimeConfig: () => ({ APP_URL: 'https://api.dev.tucana.sibel.health' }),
}));

const server = setupServer(
  rest.put('https://api.dev.tucana.sibel.health/web/bed-group/batch', (req, res, ctx) => {
    return res(ctx.status(200));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

const getGroupsMockWithData = () => {
  return cloneDeep(MockGroups);
};
const getGroupsMockWithoutData = () => {
  return [];
};

const closeMock = jest.fn();

describe('GroupManagementModal', () => {
  it('shows assigned beds in a group', async () => {
    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
    }));

    mockUseBeds.mockImplementation(() => ({
      data: MockBeds,
    }));

    mockUseGroups.mockImplementation(() => ({
      data: getGroupsMockWithData(),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            autoPlayActivated: true,
            setAutoPlayActivated: jest.fn(),
          }}
        >
          <PatientsData.Provider
            value={{
              updateActiveGroup: jest.fn(),
            }}
          >
            <GroupManagementModal isOpen onClose={closeMock} />
          </PatientsData.Provider>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    await waitFor(
      () => expect(screen.getByRole('textbox', { name: 'Group 5' })).toBeInTheDocument(),
      {
        timeout: 500,
      }
    );
    fireEvent.click(screen.getByRole('textbox', { name: 'Group 5' }));
    expect(screen.getByRole('textbox', { name: 'Group 5' })).toHaveClass('active');
    expect(screen.getByRole('row', { name: 'Bed 1 N/A' })).toBeInTheDocument();
    expect(screen.getByRole('checkbox', { name: 'Bed 1-checkbox' })).toBeChecked();
    expect(screen.getByRole('checkbox', { name: 'Bed 2-checkbox' })).not.toBeChecked();
  });

  it('shows error when bed assignment fails', async () => {
    const requestSpy = jest.fn();
    server.events.on('request:start', requestSpy);
    const deleteGroupsBatchMock = jest.fn().mockResolvedValue(true);

    jest.spyOn(managementApi, 'assignBedsToGroupsBatch').mockRejectedValue({
      response: {
        data: {
          detail: [
            {
              msg: 'Bed group not found.',
            },
          ],
        },
      },
    });
    jest.spyOn(managementApi, 'deleteGroupsBatch').mockImplementation(deleteGroupsBatchMock);
    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
    }));

    mockUseBeds.mockImplementation(() => ({
      data: MockBeds,
      refetch: jest.fn().mockResolvedValue(MockBeds),
    }));

    mockUseGroups.mockImplementation(() => ({
      data: getGroupsMockWithData(),
      refetch: jest.fn().mockResolvedValue({
        data: getGroupsMockWithData(),
      }),
      isError: false,
      isFetching: false,
      isPlaceholderData: false,
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            autoPlayActivated: true,
            setAutoPlayActivated: jest.fn(),
          }}
        >
          <PatientsData.Provider
            value={{
              updateActiveGroup: jest.fn(),
            }}
          >
            <GroupManagementModal isOpen onClose={closeMock} />
          </PatientsData.Provider>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    await waitFor(() =>
      expect(screen.getByRole('textbox', { name: 'Group 5' })).toBeInTheDocument()
    );
    fireEvent.click(screen.getByRole('textbox', { name: 'Group 5' }));
    expect(screen.getByRole('textbox', { name: 'Group 5' })).toHaveClass('active');
    expect(screen.getByRole('row', { name: 'Bed 1 N/A' })).toBeInTheDocument();
    expect(screen.queryByRole('row', { name: 'Bed 2 N/A' })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('checkbox', { name: 'Bed 2-checkbox' }));
    expect(screen.getByRole('checkbox', { name: 'Bed 2-checkbox' })).toBeChecked();
    expect(screen.getByRole('button', { name: 'Finish Setup' })).not.toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Finish Setup' }));
    await waitFor(() => {
      expect(requestSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          method: 'PUT',
          url: new URL('https://api.dev.tucana.sibel.health/web/bed-group/batch'),
        })
      );
      expect(deleteGroupsBatchMock).not.toHaveBeenCalled();
    });
  });

  it('shows error message when all beds unassigned from a group', async () => {
    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
    }));

    mockUseBeds.mockImplementation(() => ({
      data: MockBeds,
    }));
    mockUseGroups.mockImplementation(() => ({
      data: getGroupsMockWithData(),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            autoPlayActivated: true,
            setAutoPlayActivated: jest.fn(),
          }}
        >
          <PatientsData.Provider
            value={{
              updateActiveGroup: jest.fn(),
            }}
          >
            <GroupManagementModal isOpen onClose={closeMock} />
          </PatientsData.Provider>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    await waitFor(
      () => expect(screen.getByRole('textbox', { name: 'Group 5' })).toBeInTheDocument(),
      {
        timeout: 500,
      }
    );
    fireEvent.click(screen.getByRole('textbox', { name: 'Group 5' }));
    expect(screen.getByRole('row', { name: 'Bed 1 N/A' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('checkbox', { name: 'Bed 1-checkbox' }));
    expect(screen.getByText('Please first add beds to this group.')).toBeInTheDocument();
  });

  it('assigns beds in a group', async () => {
    const assignBedsToGroupsBatchMock = jest.fn();

    jest
      .spyOn(managementApi, 'assignBedsToGroupsBatch')
      .mockImplementation(assignBedsToGroupsBatchMock);
    jest.spyOn(managementApi, 'deleteGroupsBatch').mockImplementation(jest.fn());

    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
    }));

    mockUseBeds.mockImplementation(() => ({
      data: MockBeds,
      refetch: jest.fn().mockResolvedValue(MockBeds),
    }));

    mockUseGroups.mockImplementation(() => ({
      data: getGroupsMockWithData(),
      refetch: jest.fn().mockResolvedValue({ data: getGroupsMockWithData() }),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            autoPlayActivated: true,
            setAutoPlayActivated: jest.fn(),
          }}
        >
          <PatientsData.Provider
            value={{
              updateActiveGroup: jest.fn(),
            }}
          >
            <GroupManagementModal isOpen onClose={closeMock} />
          </PatientsData.Provider>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    await waitFor(
      () => expect(screen.getByRole('textbox', { name: 'Group 5' })).toBeInTheDocument(),
      {
        timeout: 500,
      }
    );
    fireEvent.click(screen.getByRole('textbox', { name: 'Group 5' }));
    expect(screen.getByRole('textbox', { name: 'Group 5' })).toHaveClass('active');
    expect(screen.getByRole('row', { name: 'Bed 1 N/A' })).toBeInTheDocument();
    expect(screen.queryByRole('row', { name: 'Bed 2 N/A' })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('checkbox', { name: 'Bed 2-checkbox' }));
    expect(screen.getByRole('checkbox', { name: 'Bed 2-checkbox' })).toBeChecked();
    expect(screen.getByRole('button', { name: 'Finish Setup' })).not.toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Finish Setup' }));
    const newMockGroups = [...MockGroups];
    newMockGroups[newMockGroups.length - 1].beds = [
      ...newMockGroups[newMockGroups.length - 1].beds,
      MockBeds[1],
    ];
    await waitFor(() => expect(assignBedsToGroupsBatchMock).toHaveBeenCalledWith(newMockGroups), {
      timeout: 500,
    });
  }, 10000);

  /*
   * Requirement IDs: RQ-00022-B: SR-1.2.4.45
   */
  it('assigns beds to new group', async () => {
    const assignBedsToGroupsBatchMock = jest.fn();

    jest
      .spyOn(managementApi, 'assignBedsToGroupsBatch')
      .mockImplementation(assignBedsToGroupsBatchMock);
    jest.spyOn(managementApi, 'deleteGroupsBatch').mockImplementation(jest.fn());

    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
    }));

    mockUseBeds.mockImplementation(() => ({
      data: MockBeds,
    }));

    mockUseGroups.mockImplementation(() => ({
      data: getGroupsMockWithData(),
      refetch: jest.fn().mockResolvedValue({
        data: getGroupsMockWithData(),
      }),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            autoPlayActivated: true,
            setAutoPlayActivated: jest.fn(),
          }}
        >
          <PatientsData.Provider
            value={{
              updateActiveGroup: jest.fn(),
            }}
          >
            <GroupManagementModal
              isOpen
              onClose={closeMock}
              bedGroups={{
                data: getGroupsMockWithData(),
                refetch: jest.fn().mockResolvedValue({
                  data: getGroupsMockWithData(),
                  refetch: jest.fn().mockResolvedValue(),
                  isError: false,
                  isFetching: false,
                  isPlaceholderData: false,
                }),
                isError: false,
                isFetching: false,
                isPlaceholderData: false,
              }}
            />
          </PatientsData.Provider>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    await waitFor(
      () => expect(screen.getByRole('textbox', { name: 'Group 5' })).toBeInTheDocument(),
      {
        timeout: 500,
      }
    );
    fireEvent.click(screen.getByTestId('add-group'));
    fireEvent.click(screen.getByRole('checkbox', { name: 'Bed 1-checkbox' }));
    expect(screen.getByLabelText('Group 6')).toBeInTheDocument();

    expect(screen.getByRole('button', { name: 'Finish Setup' })).not.toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Finish Setup' }));
    await waitFor(() => expect(assignBedsToGroupsBatchMock).toHaveBeenCalled(), {
      timeout: 500,
    });
  });

  it('renders all components', async () => {
    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
    }));

    mockUseBeds.mockImplementation(() => ({
      data: MockBeds,
    }));

    mockUseGroups.mockImplementation(() => ({
      data: getGroupsMockWithoutData(),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            autoPlayActivated: true,
            setAutoPlayActivated: jest.fn(),
          }}
        >
          <PatientsData.Provider
            value={{
              updateActiveGroup: jest.fn(),
            }}
          >
            <GroupManagementModal isOpen onClose={closeMock} />
          </PatientsData.Provider>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    await waitFor(() => expect(screen.getByText('Group Management')).toBeInTheDocument(), {
      timeout: 1000,
    });
    await waitFor(
      () => expect(screen.getByRole('button', { name: 'Finish Setup' })).toBeInTheDocument(),
      {
        timeout: 1000,
      }
    );
    expect(screen.getByRole('button', { name: 'Finish Setup' })).toBeDisabled();
    expect(screen.getByText('Groups (0)')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Delete group' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Edit group name' })).not.toBeInTheDocument();
    expect(screen.getByText('Add a group to start.')).toBeInTheDocument();
    expect(screen.getByText('Beds (0)')).toBeInTheDocument();
    expect(screen.getByText('0/16 Selected')).toBeInTheDocument();
    expect(screen.getByText('Available after initial group added.')).toBeInTheDocument();
  });

  it('handles modal dismiss', async () => {
    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
    }));

    mockUseBeds.mockImplementation(() => ({
      data: MockBeds,
    }));

    mockUseGroups.mockImplementation(() => ({
      data: getGroupsMockWithData(),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            autoPlayActivated: true,
            setAutoPlayActivated: jest.fn(),
          }}
        >
          <PatientsData.Provider
            value={{
              updateActiveGroup: jest.fn(),
            }}
          >
            <GroupManagementModal isOpen onClose={closeMock} />
          </PatientsData.Provider>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    await waitFor(() => expect(screen.getByTestId('dismiss-modal')).toBeInTheDocument(), {
      timeout: 500,
    });
    fireEvent.click(screen.getByTestId('dismiss-modal'));
    expect(closeMock).toHaveBeenCalled();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.2.4.30, SR-1.2.4.31 RQ-00022-B: SR-1.8.3.2, SR-1.8.3.3
   */
  it('detects unsaved changes', async () => {
    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
    }));

    mockUseBeds.mockImplementation(() => ({
      data: MockBeds,
    }));

    mockUseGroups.mockImplementation(() => ({
      data: getGroupsMockWithData(),
    }));

    const onCloseMock = jest.fn();

    render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            autoPlayActivated: true,
            setAutoPlayActivated: jest.fn(),
          }}
        >
          <PatientsData.Provider
            value={{
              updateActiveGroup: jest.fn(),
            }}
          >
            <GroupManagementModal isOpen onClose={onCloseMock} />
          </PatientsData.Provider>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    await waitFor(
      () => expect(screen.getByRole('textbox', { name: 'Group 1' })).toBeInTheDocument(),
      {
        timeout: 500,
      }
    );
    fireEvent.click(screen.getByRole('textbox', { name: 'Group 1' }));
    fireEvent.click(screen.getByRole('checkbox', { name: 'Bed 1-checkbox' }));

    fireEvent.click(screen.getByTestId('dismiss-modal'));
    await waitFor(() => {
      expect(screen.getByText('Unsaved information')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: 'Back to edit' }));
    await waitFor(() => {
      expect(screen.queryByText('Unsaved information')).not.toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('dismiss-modal'));
    fireEvent.click(screen.getByRole('button', { name: 'Discard' }));
    await waitFor(() => {
      expect(onCloseMock).toHaveBeenCalled();
    });
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.2.4.8
   */
  it('adds group', async () => {
    const requestSpy = jest.fn();
    server.events.on('request:start', requestSpy);

    jest.spyOn(managementApi, 'assignBedsToGroupsBatch').mockImplementation(jest.fn());
    jest.spyOn(managementApi, 'deleteGroupsBatch').mockImplementation(jest.fn());

    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
    }));

    mockUseBeds.mockImplementation(() => ({
      data: MockBeds,
    }));

    mockUseGroups.mockImplementation(() => ({
      data: [
        {
          id: 'group_2',
          name: 'Group 2',
          beds: MockBeds.slice(0, 8),
        },
      ],
      refetch: jest.fn().mockResolvedValue({
        data: [
          {
            id: 'group_2',
            name: 'Group 2',
            beds: MockBeds.slice(0, 8),
          },
        ],
      }),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            autoPlayActivated: true,
            setAutoPlayActivated: jest.fn(),
          }}
        >
          <PatientsData.Provider
            value={{
              updateActiveGroup: jest.fn(),
            }}
          >
            <GroupManagementModal isOpen onClose={jest.fn()} />
          </PatientsData.Provider>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    await waitFor(() => expect(screen.getByTestId('add-group')).toBeInTheDocument(), {
      timeout: 500,
    });
    fireEvent.click(screen.getByTestId('add-group'));
    expect(screen.queryByText('Add a group to start.')).not.toBeInTheDocument();
    expect(screen.getByText('Add beds to this group.')).toBeInTheDocument();
    expect(screen.getByText('0 total')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('checkbox', { name: 'Bed 16-checkbox' }));
    expect(screen.getByRole('button', { name: 'Finish Setup' })).not.toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Finish Setup' }));
    await waitFor(() => {
      expect(screen.getByTestId('Confirm')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));
    await waitFor(() => {
      expect(requestSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          method: 'PUT',
          url: new URL('https://api.dev.tucana.sibel.health/web/bed-group/batch'),
        })
      );
    });
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.2.4.37 RQ-00022-B: SR-1.2.4.28
   */
  it('prevents adding new group is existing group has no beds assigned', async () => {
    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
    }));

    mockUseBeds.mockImplementation(() => ({
      data: MockBeds,
    }));

    mockUseGroups.mockImplementation(() => ({
      data: getGroupsMockWithData(),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            autoPlayActivated: true,
            setAutoPlayActivated: jest.fn(),
          }}
        >
          <PatientsData.Provider
            value={{
              updateActiveGroup: jest.fn(),
            }}
          >
            <GroupManagementModal isOpen onClose={closeMock} />
          </PatientsData.Provider>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    await waitFor(() => expect(screen.getByTestId('add-group')).toBeInTheDocument(), {
      timeout: 500,
    });
    // add group without beds
    expect(screen.getByTestId('add-group')).toBeInTheDocument();
    fireEvent.click(screen.getByTestId('add-group'));
    expect(screen.getByLabelText('Group 6')).toHaveClass('active');
    fireEvent.change(screen.getByLabelText('Group 6'), 'Group 1');
    fireEvent.blur(screen.getByLabelText('Group 6'));
    expect(screen.queryByText('Add a group to start.')).not.toBeInTheDocument();
    // try adding new group
    fireEvent.click(screen.getByTestId('add-group'));
    expect(screen.getByText('Please first add beds to this group.')).toBeInTheDocument();
    // add beds to a group
    fireEvent.click(screen.getByLabelText('Group 1'));
    fireEvent.click(screen.getByRole('checkbox', { name: 'Bed 2-checkbox' }));
    expect(screen.getByRole('row', { name: 'Bed 2 N/A' })).toBeInTheDocument();
    // try adding new group
    fireEvent.click(screen.getByTestId('add-group'));
    expect(screen.queryByText('Please first add beds to this group.')).not.toBeInTheDocument();
  });

  it('generates unique group name', async () => {
    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
    }));

    mockUseBeds.mockImplementation(() => ({
      data: MockBeds,
    }));
    mockUseGroups.mockImplementation(() => ({
      data: getGroupsMockWithData(),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            autoPlayActivated: true,
            setAutoPlayActivated: jest.fn(),
          }}
        >
          <PatientsData.Provider
            value={{
              updateActiveGroup: jest.fn(),
            }}
          >
            <GroupManagementModal isOpen onClose={closeMock} />
          </PatientsData.Provider>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    await waitFor(() => expect(screen.getByTestId('add-group')).toBeInTheDocument(), {
      timeout: 500,
    });
    fireEvent.click(screen.getByTestId('add-group'));
    expect(screen.getByLabelText('Group 6')).toBeInTheDocument();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.2.4.9
   */
  it('handles active group', async () => {
    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
    }));

    mockUseBeds.mockImplementation(() => ({
      data: MockBeds,
    }));

    mockUseGroups.mockImplementation(() => ({
      data: getGroupsMockWithData(),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            autoPlayActivated: true,
            setAutoPlayActivated: jest.fn(),
          }}
        >
          <PatientsData.Provider
            value={{
              updateActiveGroup: jest.fn(),
            }}
          >
            <GroupManagementModal isOpen onClose={closeMock} />
          </PatientsData.Provider>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    await waitFor(
      () => expect(screen.getByText(`Groups (${MockGroups.length})`)).toBeInTheDocument(),
      {
        timeout: 500,
      }
    );

    for (let i = 0; i < MockGroups.length; i++) {
      expect(screen.getAllByRole('textbox')[i].value).toEqual(MockGroups[i].name);
      expect(screen.getAllByRole('textbox')[i]).toBeDisabled();
    }
    fireEvent.click(screen.getAllByRole('textbox')[0]);
    expect(screen.getAllByRole('textbox')[0]).toHaveClass('active');
    expect(screen.getByText('Beds (16)')).toBeInTheDocument();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.2.4.10, SR-1.2.4.12
   */
  it('edits group name', async () => {
    const requestSpy = jest.fn();
    server.events.on('request:start', requestSpy);
    jest.spyOn(managementApi, 'assignBedsToGroupsBatch').mockImplementation(jest.fn());
    jest.spyOn(managementApi, 'deleteGroupsBatch').mockImplementation(jest.fn());

    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
    }));

    mockUseBeds.mockImplementation(() => ({
      data: MockBeds,
    }));

    mockUseGroups.mockImplementation(() => ({
      data: getGroupsMockWithData(),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            autoPlayActivated: true,
            setAutoPlayActivated: jest.fn(),
          }}
        >
          <PatientsData.Provider
            value={{
              updateActiveGroup: jest.fn(),
            }}
          >
            <GroupManagementModal isOpen onClose={closeMock} />
          </PatientsData.Provider>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    await waitFor(
      () => expect(screen.getByRole('textbox', { name: 'Group 5' })).toBeInTheDocument(),
      {
        timeout: 500,
      }
    );
    await waitFor(() => expect(screen.getByText('Groups (5)')).toBeInTheDocument(), {
      timeout: 500,
    });
    fireEvent.click(screen.getByLabelText('Group 1'));
    fireEvent.click(screen.getByRole('button', { name: 'Edit group name' }));
    fireEvent.change(screen.getByLabelText('Group 1'), { target: { value: 'Group 6' } });
    fireEvent.blur(screen.getByLabelText('Group 1'));
    expect(screen.getByRole('button', { name: 'Finish Setup' })).not.toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Finish Setup' }));

    await waitFor(() => {
      expect(requestSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          method: 'PUT',
          url: new URL('https://api.dev.tucana.sibel.health/web/bed-group/batch'),
        })
      );
    });
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.2.4.13
   */
  it('deletes group', async () => {
    const deleteGroupsBatchMock = jest.fn();
    jest.spyOn(managementApi, 'deleteGroupsBatch').mockImplementation(deleteGroupsBatchMock);

    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
    }));

    mockUseBeds.mockImplementation(() => ({
      data: MockBeds,
    }));

    mockUseGroups.mockImplementation(() => ({
      data: getGroupsMockWithData(),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            autoPlayActivated: true,
            setAutoPlayActivated: jest.fn(),
          }}
        >
          <PatientsData.Provider
            value={{
              updateActiveGroup: jest.fn(),
            }}
          >
            <GroupManagementModal isOpen onClose={closeMock} />
          </PatientsData.Provider>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    await waitFor(() => expect(screen.getByText('Groups (5)')).toBeInTheDocument(), {
      timeout: 500,
    });
    fireEvent.click(screen.getAllByRole('textbox')[0]);
    fireEvent.click(screen.getByRole('button', { name: 'Delete group' }));
    expect(screen.getByText('Groups (4)')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Finish Setup' }));
    expect(screen.getByText('Confirmation required')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));
    expect(deleteGroupsBatchMock).toHaveBeenCalledWith(['group_1']);
    expect(screen.queryByText('Failed to modify bed groups')).not.toBeInTheDocument();
  });

  it('shows error message when failed to delete group', async () => {
    jest
      .spyOn(managementApi, 'deleteGroupsBatch')
      .mockRejectedValueOnce(new Error('failed to delete'));

    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
    }));

    mockUseBeds.mockImplementation(() => ({
      data: MockBeds,
    }));

    mockUseGroups.mockImplementation(() => ({
      data: getGroupsMockWithData(),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            autoPlayActivated: true,
            setAutoPlayActivated: jest.fn(),
          }}
        >
          <PatientsData.Provider
            value={{
              updateActiveGroup: jest.fn(),
            }}
          >
            <GroupManagementModal isOpen onClose={closeMock} />
          </PatientsData.Provider>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    await waitFor(() => expect(screen.getByText('Groups (5)')).toBeInTheDocument(), {
      timeout: 500,
    });
    fireEvent.click(screen.getAllByRole('textbox')[0]);
    fireEvent.click(screen.getByRole('button', { name: 'Delete group' }));
    expect(screen.getByText('Groups (4)')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Finish Setup' }));
    expect(screen.getByText('Confirmation required')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Confirm' }));
    await waitFor(
      () => expect(screen.getByText('Failed to modify bed groups')).toBeInTheDocument(),
      {
        timeout: 500,
      }
    );
    fireEvent.click(screen.getByRole('button', { name: 'OK' }));
    expect(screen.queryByText('Failed to modify bed groups')).not.toBeInTheDocument();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.2.4.39
   */
  it('shows error message when failed to fetch groups', async () => {
    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
    }));

    mockUseGroups.mockImplementation(() => ({
      data: [],
      refetch: jest.fn().mockRejectedValue(new Error('failed to fetch')),
      isError: true,
      isFetching: false,
      isPlaceholderData: false,
    }));

    mockUseBeds.mockImplementation(() => ({
      data: MockBeds,
      refetch: jest.fn().mockResolvedValue(MockBeds),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            autoPlayActivated: true,
            setAutoPlayActivated: jest.fn(),
          }}
        >
          <PatientsData.Provider
            value={{
              updateActiveGroup: jest.fn(),
            }}
          >
            <GroupManagementModal
              isOpen
              onClose={closeMock}
              bedGroups={{
                data: [],
                refetch: jest.fn().mockRejectedValue(new Error('failed to fetch')),
                isError: true,
                isFetching: false,
                isPlaceholderData: false,
              }}
            />
          </PatientsData.Provider>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    await waitFor(
      () =>
        expect(
          screen.getByText('Failed to display bed groups. Please try again in a few minutes.')
        ).toBeInTheDocument(),
      {
        timeout: 500,
      }
    );
  });

  it('unassigns beds in a group', async () => {
    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
    }));

    mockUseBeds.mockImplementation(() => ({
      data: MockBeds,
    }));

    mockUseGroups.mockImplementation(() => ({
      data: getGroupsMockWithData(),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            autoPlayActivated: true,
            setAutoPlayActivated: jest.fn(),
          }}
        >
          <PatientsData.Provider
            value={{
              updateActiveGroup: jest.fn(),
            }}
          >
            <GroupManagementModal isOpen onClose={closeMock} />
          </PatientsData.Provider>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    await waitFor(
      () => expect(screen.getByRole('textbox', { name: 'Group 1' })).toBeInTheDocument(),
      {
        timeout: 500,
      }
    );
    fireEvent.click(screen.getByRole('textbox', { name: 'Group 1' }));
    expect(screen.getByRole('textbox', { name: 'Group 1' })).toHaveClass('active');
    expect(screen.getByRole('row', { name: 'Bed 1 N/A' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('checkbox', { name: 'Bed 1-checkbox' }));
    expect(screen.getByRole('checkbox', { name: 'Bed 1-checkbox' })).not.toBeChecked();
    expect(screen.queryByRole('row', { name: 'Bed 1 N/A' })).not.toBeInTheDocument();
  });

  /*
   * Requirement IDs: RQ-00022-B: SR-1.2.4.30, SR-1.2.4.32 RQ-00022-B: SR-1.2.4.30
   */
  it('shows finish setup modal -> has unassigned bed', async () => {
    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
    }));

    mockUseBeds.mockImplementation(() => ({
      data: MockBeds,
    }));

    mockUseGroups.mockImplementation(() => ({
      data: getGroupsMockWithData(),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            autoPlayActivated: true,
            setAutoPlayActivated: jest.fn(),
          }}
        >
          <PatientsData.Provider
            value={{
              updateActiveGroup: jest.fn(),
            }}
          >
            <GroupManagementModal isOpen onClose={closeMock} />
          </PatientsData.Provider>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    await waitFor(
      () => expect(screen.getByRole('textbox', { name: 'Group 1' })).toBeInTheDocument(),
      {
        timeout: 500,
      }
    );
    fireEvent.click(screen.getByRole('textbox', { name: 'Group 1' }));
    fireEvent.click(screen.getByRole('checkbox', { name: 'Bed 16-checkbox' }));

    fireEvent.click(screen.getByRole('button', { name: 'Finish Setup' }));
    await waitFor(() => {
      expect(screen.getByText('Confirmation required')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: 'Back to edit' }));
    expect(screen.queryByText('Confirmation required')).not.toBeInTheDocument();
  });

  it('does not show finish setup modal -> has no unassigned bed', async () => {
    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
    }));

    mockUseBeds.mockImplementation(() => ({
      data: MockBeds,
    }));

    mockUseGroups.mockImplementation(() => ({
      data: getGroupsMockWithData(),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            autoPlayActivated: true,
            setAutoPlayActivated: jest.fn(),
          }}
        >
          <PatientsData.Provider
            value={{
              updateActiveGroup: jest.fn(),
            }}
          >
            <GroupManagementModal isOpen onClose={closeMock} />
          </PatientsData.Provider>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    await waitFor(
      () => expect(screen.getByRole('button', { name: 'Finish Setup' })).toBeInTheDocument(),
      {
        timeout: 500,
      }
    );
    fireEvent.click(screen.getByRole('button', { name: 'Finish Setup' }));
    await waitFor(() => {
      expect(screen.queryByText('Confirmation required')).not.toBeInTheDocument();
    });
  });

  it('submit group', async () => {
    const assignBedsToGroupsBatchMock = jest.fn().mockResolvedValue({
      status: 204,
      data: {},
      statusText: 'OK',
      config: {},
      headers: {},
    });
    jest
      .spyOn(managementApi, 'assignBedsToGroupsBatch')
      .mockImplementation(assignBedsToGroupsBatchMock);

    mockUsePatientMonitors.mockImplementation(() => ({
      data: [],
    }));

    mockUseBeds.mockImplementation(() => ({
      data: MockBeds,
    }));

    mockUseGroups.mockImplementation(() => ({
      data: getGroupsMockWithData(),
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <AudioManager.Provider
          value={{
            autoPlayActivated: true,
            setAutoPlayActivated: jest.fn(),
          }}
        >
          <PatientsData.Provider
            value={{
              updateActiveGroup: jest.fn(),
            }}
          >
            <GroupManagementModal isOpen onClose={closeMock} />
          </PatientsData.Provider>
        </AudioManager.Provider>
      </QueryClientProvider>
    );

    await waitFor(() => expect(screen.getByText('Beds (16)')).toBeInTheDocument(), {
      timeout: 1500,
    });
    fireEvent.click(screen.getByRole('textbox', { name: 'Group 2' }));
    fireEvent.click(screen.getByRole('button', { name: 'Delete group' }));

    fireEvent.click(screen.getByRole('textbox', { name: 'Group 4' }));
    fireEvent.click(screen.getByRole('button', { name: 'Edit group name' }));
    fireEvent.change(screen.getByRole('textbox', { name: 'Group 4' }), 'Group 2');
    fireEvent.blur(screen.getByRole('textbox', { name: 'Group 4' }));

    fireEvent.click(screen.getByRole('button', { name: 'Finish Setup' }));

    await waitFor(() => {
      expect(screen.queryByText('Confirmation required')).not.toBeInTheDocument();
    });
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });
});
