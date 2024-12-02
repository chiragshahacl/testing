import { assignBedsToGroupsBatch, deleteGroupsBatch } from '@/api/managementApi';
import { useUpdateGroupBatch } from '@/api/useUpdateGroupBatch';
import AddGroupIcon from '@/components/icons/AddGroupIcon';
import AddIcon from '@/components/icons/AddIcon';
import BedIcon from '@/components/icons/BedIcon';
import GroupIcon from '@/components/icons/GroupIcon';
import EditableHorizontalList from '@/components/lists/EditableHorizontalList';
import TableList from '@/components/lists/TableList';
import TableListWithCheckbox from '@/components/lists/TableListWithCheckbox';
import ModalContainer from '@/components/modals/container/ModalContainer';
import { bedManagementErrors, groupManagementErrors } from '@/constants';
import useAudioManager from '@/hooks/useAudioManager';
import usePatientData from '@/hooks/usePatientsData';
import { Content, ContentHeader } from '@/styles/StyledComponents';
import { BedType } from '@/types/bed';
import { GroupType, NewGroupType } from '@/types/group';
import { styled } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { v4 as uuid4 } from 'uuid';
import { cloneDeep, get, isEqual } from 'lodash';
import { useCallback, useEffect, useState } from 'react';
import FinishSetupConfirmationModal from './FinishSetupConfirmationModal';
import ModifyServerErrorModal from './ModifyServerErrorModal';
import UnsavedModal from './UnsavedModal';
import { useBeds } from '@/api/useBeds';
import { useGroups } from '@/api/useGroups';

const ButtonTitle = styled(Typography)(({ theme }) => ({
  fontSize: 18,
  fontWeight: '700',
  margin: theme.spacing(0, 11),
  color: theme.palette.primary.light,
}));

interface GroupManagementModalProps {
  onClose: () => void;
  isOpen: boolean;
}

const DEFAULT_GROUP: GroupType = { id: '', beds: [], name: '' };

const GroupManagementModal = ({ onClose, isOpen }: GroupManagementModalProps) => {
  const beds = useBeds();
  const bedGroups = useGroups();
  const { updateActiveGroup } = usePatientData();
  const { autoPlayActivated, setAutoPlayActivated } = useAudioManager();

  const [selectedGroupId, setSelectedGroupId] = useState<string | undefined>(
    bedGroups?.data && bedGroups.data.length > 0 ? bedGroups.data[0].id : undefined
  );
  const [tempGroupsBeds, setTempGroupsBeds] = useState<GroupType[]>([]);
  const [showConfirmationModal, setShowConfirmationModal] = useState(false);
  const [editingGroup, setEditingGroup] = useState<boolean>(false);
  const [showUnsavedModal, setShowUnsavedModal] = useState<boolean>(false);
  const [hasErrorInGroupName, setHasErrorInGroupName] = useState<Record<string, boolean>>({});
  const [groupErrors, setGroupErrors] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [showGroupModifyError, setShowGroupModifyError] = useState<boolean>(false);

  const updateGroupBatch = useUpdateGroupBatch();

  const addError = useCallback(
    (newError: string) => {
      if (!groupErrors.includes(newError)) setGroupErrors([...groupErrors, newError]);
    },
    [groupErrors]
  );

  const removeError = useCallback(
    (errorToRemove: string) => {
      if (groupErrors.includes(errorToRemove))
        setGroupErrors(groupErrors.filter((error) => error !== errorToRemove));
    },
    [groupErrors]
  );

  const clearServerErrors = () => {
    const nonServerErrors = [
      groupManagementErrors['emptyGroup'],
      groupManagementErrors['duplicateGroup'],
    ];
    const cleanedErrors = groupErrors.filter((error) => nonServerErrors.includes(error));
    setGroupErrors(cleanedErrors);
  };

  const handleSelectGroup = (groupId: string) => {
    clearServerErrors();
    if (selectedGroupId && getSelectedGroup().beds.length === 0)
      addError(groupManagementErrors['emptyGroup']);
    else if (
      ((selectedGroupId && !hasErrorInGroupName[selectedGroupId]) ||
        groupErrors.indexOf(groupManagementErrors['emptyGroup']) < 0) &&
      getSelectedGroup().name
    )
      setSelectedGroupId(groupId);
  };

  const getSelectedGroup = () => {
    return tempGroupsBeds.find((group) => group.id === selectedGroupId) || DEFAULT_GROUP;
  };

  const assignBedToGroup = (bedId: string) => {
    clearServerErrors();
    if (selectedGroupId) {
      removeError(groupManagementErrors['emptyGroup']);
      const bedToAdd: BedType | null = beds.data.find((bed: BedType) => bed.id === bedId) || null;
      const modifiedGroups = tempGroupsBeds.map((group) => {
        if (group.id === selectedGroupId && bedToAdd) {
          group.beds = [...group.beds, bedToAdd];
        }
        return group;
      });

      if (modifiedGroups && bedToAdd) {
        setTempGroupsBeds(modifiedGroups);
      }
    }
  };

  const restoreBedGroups = useCallback(() => {
    setTempGroupsBeds(cloneDeep(bedGroups.data) || []);
    setSelectedGroupId(bedGroups.data[0]?.id);
  }, [bedGroups.data]);

  const unassignBedFromGroup = (removeBedId: string) => {
    clearServerErrors();
    const modifiedGroups = tempGroupsBeds.map((group) => {
      if (group.id === selectedGroupId) {
        group.beds = group.beds.filter((bed: BedType) => bed.id !== removeBedId);
      }
      return group;
    });
    if (
      tempGroupsBeds.find((group: GroupType) => {
        return group.beds.length === 0;
      })
    ) {
      addError(groupManagementErrors['emptyGroup']);
    }
    setTempGroupsBeds(modifiedGroups);
  };

  const addGroup = () => {
    clearServerErrors();
    if (tempGroupsBeds.length !== 0 && selectedGroupId && getSelectedGroup().beds.length === 0) {
      addError(groupManagementErrors['emptyGroup']);
    } else {
      removeError(groupManagementErrors['emptyGroup']);
      let newGroupNo: number = tempGroupsBeds.length;
      let groupName = '';
      let nameIsUnique = false;
      while (!nameIsUnique) {
        newGroupNo += 1;
        groupName = `Group ${newGroupNo}`;
        if (tempGroupsBeds.findIndex((group) => group.name === groupName) < 0) nameIsUnique = true;
      }
      const newGroupId = `new_${uuid4()}`;
      setTempGroupsBeds([...tempGroupsBeds, { id: newGroupId, name: groupName, beds: [] }]);
      setSelectedGroupId(newGroupId);
      setEditingGroup(true);
    }
  };

  const handleDeleteGroup = () => {
    setGroupErrors([]);
    setHasErrorInGroupName({ [selectedGroupId as string]: false });
    const newGroups = [...tempGroupsBeds];
    const index = newGroups.findIndex((group) => group.id === selectedGroupId);
    if (index > -1) {
      newGroups.splice(index, 1);
    }
    setTempGroupsBeds(newGroups);
    setSelectedGroupId(tempGroupsBeds.filter((group) => group.id !== selectedGroupId)[0]?.id);
  };

  const editGroup = () => {
    setEditingGroup(true);
  };

  const validateGroupName = (id: string, name: string) => {
    setHasErrorInGroupName({
      ...hasErrorInGroupName,
      [id]: !name || !!tempGroupsBeds.find((group) => group.name === name && group.id !== id),
    });
  };

  const editGroupName = (id: string, name: string) => {
    clearServerErrors();
    setEditingGroup(false);
    if (name) {
      const copyTempGroupsBeds = [...tempGroupsBeds];
      const groupIndex = tempGroupsBeds.findIndex((group) => group.id === id);
      if (groupIndex > -1) {
        copyTempGroupsBeds[groupIndex] = { ...tempGroupsBeds[groupIndex], name };
        setTempGroupsBeds(copyTempGroupsBeds);
      }
      if (tempGroupsBeds.find((group) => group.name === name && group.id !== id)) {
        addError(groupManagementErrors['duplicateGroup']);
      } else {
        removeError(groupManagementErrors['duplicateGroup']);
      }
    } else {
      setEditingGroup(true); // If no name, force focus again
    }
  };

  const handleGroupsModifications = async () => {
    const groupsToAdd: NewGroupType[] = [];
    const groupsToDelete: string[] = [];
    const groupsToUpdate: GroupType[] = [];
    tempGroupsBeds.forEach((tempGroup: GroupType) => {
      if (tempGroup.id.startsWith('new_')) {
        groupsToAdd.push({ ...tempGroup, id: undefined });
      }
    });
    bedGroups.data.forEach((group: GroupType) => {
      const found: GroupType | null =
        tempGroupsBeds.find((tempGroup: GroupType) => {
          return tempGroup.id === group.id;
        }) || null;
      if (found) {
        groupsToUpdate.push(found);
      } else {
        groupsToDelete.push(group.id);
      }
    });
    if (groupsToDelete.length > 0) {
      try {
        await deleteGroupsBatch(groupsToDelete);
      } catch (error) {
        throw new Error(groupManagementErrors['deleteFailed']);
      }
    }
    if (groupsToAdd.length > 0 || groupsToUpdate.length > 0) {
      await updateGroupBatch.mutateAsync({ groupsToAdd, groupsToUpdate });

      const { data: newGroups } = await bedGroups.refetch();

      if (newGroups) {
        if (groupsToAdd.length > 0) {
          const newTempGroups = [...tempGroupsBeds];
          groupsToAdd.forEach(({ name }) => {
            const newGroupWithId = newGroups.find((group) => group.name == name);
            if (newGroupWithId) {
              const index = newTempGroups.findIndex((group) => group.name === newGroupWithId.name);
              if (index !== -1) newTempGroups[index].id = newGroupWithId.id;
            }
          });
          setTempGroupsBeds(newTempGroups);
        }

        const groupsToAssign: GroupType[] = [];
        groupsToAdd.forEach((group) => {
          const foundGroup = newGroups.find((newGroup) => newGroup.name === group.name);
          if (foundGroup) groupsToAssign.push({ ...group, id: foundGroup.id });
        });
        groupsToUpdate.forEach((group) => {
          groupsToAssign.push(group);
        });

        try {
          await assignBedsToGroupsBatch(groupsToAssign);
        } catch (error) {
          throw new Error(get(error, 'response.data.detail[0].msg', 'Something went wrong.'));
        }
      }
    }
  };

  const submitSetup = async () => {
    if (showConfirmationModal) setShowConfirmationModal(false);
    setIsLoading(true);
    try {
      await handleGroupsModifications();
      const { data: newGroups } = await bedGroups.refetch();
      if (newGroups) {
        updateActiveGroup(newGroups[0].id);
        onClose();
      }
    } catch (error) {
      setShowGroupModifyError(true);
      restoreBedGroups();
    }
    setIsLoading(false);
  };

  const handleFinishSetup = () => {
    const unasignedBeds: BedType[] = [...beds.data];
    tempGroupsBeds.forEach((group) => {
      group.beds.forEach((bed) => {
        const i = unasignedBeds.findIndex((unasignedBed) => bed.bedNo === unasignedBed.bedNo);
        if (i > -1) unasignedBeds.splice(i, 1);
      });
    });
    if (unasignedBeds.length === 0) {
      void submitSetup();
    } else {
      setShowConfirmationModal(true);
    }
  };

  const handleModalClose = () => {
    if (!isEqual(bedGroups.data, tempGroupsBeds)) {
      setShowUnsavedModal(true);
    } else {
      onClose();
    }
  };

  useEffect(() => {
    // Triggers error message when there is a failure when fetching beds
    if (bedGroups.isError) addError(groupManagementErrors['failedToFetch']);
    else removeError(groupManagementErrors['failedToFetch']);
  }, [addError, bedGroups.isError, removeError]);

  useEffect(() => {
    if (isOpen && !autoPlayActivated) {
      // Disable audio modal if group management modal is opened
      setAutoPlayActivated(true);
    }
  }, [autoPlayActivated, isOpen, setAutoPlayActivated]);

  useEffect(() => {
    // Updates shown groups when there is new data when requesting bed groups information
    if (!bedGroups.isFetching && !bedGroups.isPlaceholderData && bedGroups.data) {
      restoreBedGroups();
      setSelectedGroupId(bedGroups?.data[0]?.id);
    }
  }, [bedGroups.isFetching, bedGroups.isPlaceholderData]);

  const handleDiscard = () => {
    restoreBedGroups();
    onClose();
    setShowUnsavedModal(false);
  };

  return (
    <>
      <ModifyServerErrorModal
        title='Failed to modify bed groups'
        description='Failed to modify bed groups. Please try again in a few minutes.'
        open={showGroupModifyError}
        handleClose={() => setShowGroupModifyError(false)}
      />
      <UnsavedModal
        isOpen={showUnsavedModal}
        onContinueEdit={() => setShowUnsavedModal(false)}
        onDiscard={handleDiscard}
      />
      <FinishSetupConfirmationModal
        open={showConfirmationModal}
        handleClose={() => setShowConfirmationModal(false)}
        handleConfirm={() => void submitSetup()}
      />
      <ModalContainer
        loading={bedGroups.isFetching || isLoading}
        modalHidden={!isOpen}
        onClose={handleModalClose}
        headerTitle='Group Management'
        headerIcon={<AddGroupIcon />}
        footer={
          <Button
            data-testid='finish-setup-button'
            variant='contained'
            fullWidth
            disabled={
              Object.values(hasErrorInGroupName).some((error) => error) ||
              tempGroupsBeds.length === 0 ||
              !!tempGroupsBeds.find((group: GroupType) => {
                return group.beds.length === 0;
              })
            }
            onClick={handleFinishSetup}
          >
            Finish Setup
          </Button>
        }
      >
        <Content style={{ width: 'calc(67% - 8px)' }}>
          <ContentHeader>
            <Grid display='flex' sx={{ alignItems: 'center' }}>
              <GroupIcon />
              <Typography variant='h2'>
                {`Groups (${Object.keys(tempGroupsBeds).length})`}
              </Typography>
            </Grid>
            {Object.keys(tempGroupsBeds).length > 0 && (
              <Grid display='flex'>
                <Button variant='text' onClick={handleDeleteGroup}>
                  <ButtonTitle>Delete group</ButtonTitle>
                </Button>
                <Button variant='text' onClick={editGroup} data-testid='edit-group-name'>
                  <ButtonTitle>Edit group name</ButtonTitle>
                </Button>
              </Grid>
            )}
          </ContentHeader>
          {groupErrors.includes(groupManagementErrors['failedToFetch']) ? (
            <Typography sx={{ margin: (theme) => theme.spacing(10, 0, 8, 0) }} variant='error'>
              {groupManagementErrors['failedToFetch']}
            </Typography>
          ) : (
            <>
              <Grid display='flex' flexDirection='row'>
                <Grid display='flex' sx={{ width: 'calc(100% - 26px)' }}>
                  {Object.keys(tempGroupsBeds).length > 0 ? (
                    <EditableHorizontalList
                      items={tempGroupsBeds}
                      activeItem={selectedGroupId}
                      onItemPress={handleSelectGroup}
                      editingActiveItem={editingGroup}
                      onItemNameChange={validateGroupName}
                      onFinishEditingItem={editGroupName}
                      hasError={hasErrorInGroupName}
                    />
                  ) : (
                    <Typography>Add a group to start.</Typography>
                  )}
                </Grid>
                <Grid
                  data-testid='add-group'
                  display='flex'
                  sx={{ flex: 1, cursor: 'pointer' }}
                  justifyContent='flex-end'
                  alignItems='center'
                  onClick={addGroup}
                >
                  <AddIcon />
                </Grid>
              </Grid>
              {groupErrors.length > 0 && (
                <Typography sx={{ margin: (theme) => theme.spacing(10, 0, 8, 0) }} variant='error'>
                  {groupErrors[0]}
                </Typography>
              )}
              <Typography
                data-testid='total-beds'
                sx={{ mb: 12, ...(groupErrors.length === 0 && { mt: 14 }) }}
                variant='caption'
              >
                {`${getSelectedGroup().beds.length || 0} total `}
              </Typography>
              {getSelectedGroup().beds.length > 0 ? (
                <Box component='div' style={{ flex: 1, overflow: 'auto' }}>
                  <TableList data={getSelectedGroup().beds} />
                </Box>
              ) : (
                <Typography variant='body1'>Add beds to this group.</Typography>
              )}
            </>
          )}
        </Content>
        <Content style={{ width: 'calc(33% - 8px)' }}>
          <ContentHeader>
            <Grid display='flex' sx={{ alignItems: 'center' }}>
              <BedIcon />
              <Typography variant='h2'>
                {`Beds (${Object.keys(tempGroupsBeds).length === 0 ? 0 : beds.data.length})`}
              </Typography>
            </Grid>
            <Grid display='flex'>
              <Typography variant='body2' sx={{ alignSelf: 'center' }}>{`${
                getSelectedGroup().beds.length || 0
              }/16 Selected`}</Typography>
            </Grid>
          </ContentHeader>
          {beds.isError ? (
            <Typography sx={{ margin: (theme) => theme.spacing(10, 0, 8, 0) }} variant='error'>
              {bedManagementErrors.failedToFetch}
            </Typography>
          ) : (
            <Grid sx={{ overflow: 'auto' }}>
              {Object.keys(tempGroupsBeds).length > 0 ? (
                <TableListWithCheckbox
                  data={beds.data}
                  checkedBeds={getSelectedGroup().beds}
                  handleCheck={(bed: BedType) => {
                    assignBedToGroup(bed.id);
                  }}
                  handleUncheck={(bed: BedType) => {
                    unassignBedFromGroup(bed.id);
                  }}
                />
              ) : (
                <Typography>Available after initial group added.</Typography>
              )}
            </Grid>
          )}
        </Content>
      </ModalContainer>
    </>
  );
};

export default GroupManagementModal;
