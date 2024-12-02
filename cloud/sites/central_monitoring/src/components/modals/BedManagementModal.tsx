import { useAssignBedToMonitor } from '@/api/useAssignBedToMonitor';
import { useBeds } from '@/api/useBeds';
import { useDeleteBedBatch } from '@/api/useDeleteBedBatch';
import { usePatientMonitors } from '@/api/usePatientMonitors';
import { BedRequestType, useUpdateBedBatch } from '@/api/useUpdateBedBatch';
import BedIcon from '@/components/icons/BedIcon';
import ModalContainer from '@/components/modals/container/ModalContainer';
import AddBedsContent from '@/components/modals/content/AddBedsContent';
import { NO_ASSIGNED_VALUE, bedManagementErrors } from '@/constants';
import { BedType, DeleteBedType } from '@/types/bed';
import { BedMonitorAssociation, PatientMonitor } from '@/types/patientMonitor';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import { useTranslation } from 'react-i18next';
import { v4 as uuid4 } from 'uuid';
import { useQueryClient } from '@tanstack/react-query';
import { cloneDeep, isEqual } from 'lodash';
import { useCallback, useEffect, useState } from 'react';
import FinishBedAssignmentConfirmationModal from './FinishBedAssignmentConfirmationModal';
import ModifyServerErrorModal from './ModifyServerErrorModal';
import UnsavedModal from './UnsavedModal';
import AssignBedContent from './content/AssignBedContent';
import { styled } from '@mui/material';

interface BedManagementModalProps {
  onClose: (closeAllModals?: boolean) => void;
  isOpen: boolean;
  initialStep?: 1 | 2;
}

const BedManagementHalfTextButton = styled(Button)(() => ({
  width: '49%',
  height: '50px',
}));

const BedManagementModal = ({ isOpen, onClose, initialStep }: BedManagementModalProps) => {
  const [tempBeds, setTempBeds] = useState<BedType[]>([]);
  const [step, setStep] = useState<1 | 2>(initialStep ?? 1);
  const [errors, setErrors] = useState<Record<string, string | undefined>>({});
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isDisabled, setIsDisabled] = useState<boolean>(false);
  const [tempPatientMonitors, setTempPatientMonitors] = useState<PatientMonitor[]>([]);
  const [showConfirmModal, setShowConfirmModal] = useState<boolean>(false);
  const [showUnsavedModal, setShowUnsavedModal] = useState<boolean>(false);
  const [showModifyFailed, setShowModifyFailed] = useState<boolean>(false);
  const [serverErrorModalContent, setServerErrorModalContent] = useState<Record<string, string>>();
  const [serverError, setServerError] = useState<string | null>(null);

  const { t } = useTranslation();
  const patientMonitors = usePatientMonitors();
  const beds = useBeds();
  const assignBedToMonitor = useAssignBedToMonitor();
  const updateBedBatch = useUpdateBedBatch();
  const deleteBedBatch = useDeleteBedBatch();
  const queryClient = useQueryClient();

  const restoreBedData = useCallback(() => {
    if (beds.data) {
      setTempBeds(
        cloneDeep(beds.data).sort((firstBed, secondBed) =>
          firstBed.bedNo > secondBed.bedNo ? 1 : secondBed.bedNo > firstBed.bedNo ? -1 : 0
        )
      );
    }
  }, [beds.data]);

  const restorePatientMonitorData = useCallback(() => {
    if (patientMonitors.data) {
      setTempPatientMonitors(cloneDeep(patientMonitors.data));
    }
  }, [patientMonitors.data]);

  useEffect(() => {
    // Updates shown PMs when there is new data when requesting PMs information
    if (!patientMonitors.isFetching && !patientMonitors.isPlaceholderData && patientMonitors.data) {
      restorePatientMonitorData();
    }
  }, [patientMonitors.isFetching, patientMonitors.isPlaceholderData]);

  useEffect(() => {
    // Updates shown beds when there is new data when requesting beds information
    if (!beds.isFetching && !beds.isPlaceholderData && beds.data) {
      restoreBedData();
    }
  }, [beds.isFetching, beds.isPlaceholderData]);

  useEffect(() => {
    // Triggers error message when there is a failure when fetching beds
    if (beds.isError) {
      setServerError(bedManagementErrors['failedToFetch']);
      setTempBeds([]);
    } else {
      setServerError(null);
    }
  }, [beds.isError]);

  useEffect(() => {
    // Triggers error message when there is a failure when fetching PMs
    if (patientMonitors.isError) {
      setServerError(bedManagementErrors['failedToFetchPMs']);
      setTempPatientMonitors([]);
    } else {
      setServerError(null);
    }
  }, [patientMonitors.isError]);

  useEffect(() => {
    // Controls loading indicator
    if (patientMonitors.isFetching || beds.isFetching) {
      setIsLoading(true);
    } else {
      setIsLoading(false);
    }
  }, [patientMonitors.isFetching, beds.isFetching]);

  useEffect(() => {
    // Sets correct step when opening the modal
    if (!initialStep) {
      if (isOpen && beds.data && beds.data.length > 0) {
        setStep(2);
      } else {
        setStep(1);
      }
    }
  }, [isOpen, beds.isSuccess, beds.data, initialStep]);

  function validateBeds(): Record<string, string> {
    const newErrors: Record<string, string> = {};
    tempBeds.forEach((bed, index) => {
      let errorMsg = '';
      if (bed.bedNo === '') {
        errorMsg = bedManagementErrors.bedNoEmpty;
      } else if (
        tempBeds.find(
          (otherBed, otherIndex) =>
            bed.id !== otherBed.id &&
            bed.bedNo.trim().toUpperCase() === otherBed.bedNo.trim().toUpperCase() &&
            otherIndex < index
        )
      ) {
        errorMsg = bedManagementErrors.bedNoAlreadyExists;
      }
      if (errorMsg) {
        newErrors[bed.id] = errorMsg;
      }
    });
    setErrors(newErrors);
    return newErrors;
  }

  const handleBedsModifications = async () => {
    const bedsToDelete: DeleteBedType[] = [];
    const resources: BedRequestType[] = [];

    tempBeds.forEach((tempBed: BedType) => {
      if (tempBed.id?.startsWith('new_')) {
        resources.push({ name: tempBed.bedNo.trim() });
      }
    });

    beds.data.forEach((bed: BedType) => {
      const found: BedType | null =
        tempBeds.find((tempBed) => {
          return tempBed.id === bed.id;
        }) || null;

      if (found) {
        resources.push({ id: bed.id, name: found.bedNo.trim() });
      } else {
        bedsToDelete.push(bed.id);
      }
    });

    if (resources.length > 0)
      try {
        await updateBedBatch.mutateAsync(resources);
        void queryClient.invalidateQueries({ queryKey: ['bed'] });
        void queryClient.invalidateQueries({ queryKey: ['patient-monitors'] });
      } catch (error) {
        setServerErrorModalContent({
          title: 'Failed to modify beds',
          desc: 'Failed to modify beds. Please try again in a few minutes.',
        });
        setShowModifyFailed(true);
        restoreBedData();
      } finally {
        setIsLoading(false);
      }

    if (bedsToDelete.length > 0) {
      await deleteBedBatch.mutateAsync(bedsToDelete, {
        onError: () => {
          setServerErrorModalContent({
            title: 'Failed to modify beds',
            desc: 'Failed to modify beds. Please try again in a few minutes.',
          });
          setShowModifyFailed(true);
          restoreBedData();
        },
        onSuccess: () => {
          void queryClient.invalidateQueries({ queryKey: ['bed'] });
          void queryClient.invalidateQueries({ queryKey: ['patient-monitors'] });
        },
        onSettled: () => {
          setIsLoading(false);
        },
      });
    }

    await beds.refetch();
  };

  const handleMonitorBedAssociations = () => {
    setIsLoading(true);
    setShowConfirmModal(false);

    const bedMonitorAssociations: BedMonitorAssociation[] = patientMonitors.data
      .filter((monitor) => {
        // Find if the monitor has been assigned a new bed
        const foundMonitor = tempPatientMonitors.find(
          (tempMonitor) => tempMonitor.id === monitor.id
        );
        return monitor.assignedBedId !== foundMonitor?.assignedBedId;
      })
      .flatMap((monitor) => {
        // Map to the format required by the API for assigning beds to monitors
        const foundMonitor = tempPatientMonitors.find(
          (tempMonitor) => tempMonitor.id === monitor.id
        );
        if (!foundMonitor) return [];
        const bedId =
          foundMonitor?.assignedBedId === NO_ASSIGNED_VALUE ? null : foundMonitor?.assignedBedId;
        return {
          // eslint-disable-next-line camelcase
          bed_id: bedId,
          // eslint-disable-next-line camelcase
          device_id: foundMonitor.id,
        };
      });

    if (bedMonitorAssociations.length > 0) {
      assignBedToMonitor.mutate(bedMonitorAssociations, {
        onError: () => {
          setServerErrorModalContent({
            title: 'Failed to assign beds',
            desc: 'Failed to assign beds. Please try again in a few minutes.',
          });
          setShowModifyFailed(true);
          restorePatientMonitorData();
        },
        onSuccess: () => {
          void beds.refetch();
          void patientMonitors.refetch();
          onClose();
          setStep(1);
        },
        onSettled: () => {
          setIsLoading(false);
        },
      });
    } else {
      setStep(1);
      setIsLoading(false);
      onClose();
    }
  };

  const handleNext = async () => {
    const newErrors = validateBeds();
    if (!Object.values(newErrors).some((error) => !!error)) {
      setIsLoading(true);
      await handleBedsModifications();
      setStep(2);
      setIsLoading(false);
    }
  };

  const handleBack = () => setStep(1);

  const handleFinishSetup = () => {
    if (tempPatientMonitors.find((pm: PatientMonitor) => pm.assignedBedId === null))
      setShowConfirmModal(true);
    else handleMonitorBedAssociations();
  };

  const addTempBed = () => {
    if (tempBeds.length === 0) setIsDisabled(true);
    setTempBeds([...tempBeds, { id: `new_${uuid4()}`, bedNo: '' }]);
  };

  const modifyTempBedNo = (bedId: string, newBedNo: string) => {
    const newBeds = [...tempBeds];
    const bedIndex = tempBeds.findIndex((bed) => bed.id === bedId);
    if (bedIndex >= 0) {
      newBeds[bedIndex] = { ...newBeds[bedIndex], bedNo: newBedNo };
      setTempBeds(newBeds);
    }
    const monitorIndex = tempPatientMonitors.findIndex(
      (monitor) => monitor.assignedBedId === newBeds[bedIndex].id
    );
    if (monitorIndex >= 0) {
      const newPatientMonitors = [...tempPatientMonitors];
      newPatientMonitors[monitorIndex] = {
        ...newPatientMonitors[monitorIndex],
        assignedBedId: null,
      };
      setTempPatientMonitors(newPatientMonitors);
    }
  };

  const clearError = (bedId: string) => {
    setErrors({ ...errors, [bedId]: undefined });
  };

  const changeBedNo = (bedId: string, bedNo: string) => {
    if (tempBeds.length === 1 && bedNo === '') setIsDisabled(true);
    else setIsDisabled(false);
    clearError(bedId);
  };

  const removeTempBed = (bedId: string) => {
    const bedIndex = tempBeds.findIndex((bed) => bed.id === bedId);
    const newBeds = [...tempBeds];
    const deletedBeds = newBeds.splice(bedIndex, 1);
    if (deletedBeds.length === 1) {
      setTempBeds(newBeds);
      const monitorIndex = tempPatientMonitors.findIndex((monitor) => {
        return monitor.assignedBedId === deletedBeds[0].id;
      });
      if (monitorIndex >= 0) {
        const newPatientMonitors = [...tempPatientMonitors];
        newPatientMonitors[monitorIndex].assignedBedId = null;
        setTempPatientMonitors(newPatientMonitors);
      }
      if (newBeds.length === 1 && newBeds[0].bedNo === '') setIsDisabled(true);
      clearError(deletedBeds[0].id);
    }
  };

  const handleDiscard = () => {
    beds?.data && setTempBeds(beds?.data);
    patientMonitors?.data && setTempPatientMonitors(patientMonitors?.data);
    setShowUnsavedModal(false);
    onClose(true);
    setStep(1);
  };

  return (
    <>
      <ModifyServerErrorModal
        title={serverErrorModalContent?.title || ''}
        description={serverErrorModalContent?.desc || ''}
        open={showModifyFailed}
        handleClose={() => setShowModifyFailed(false)}
      />
      <UnsavedModal
        isOpen={showUnsavedModal}
        onContinueEdit={() => setShowUnsavedModal(false)}
        onDiscard={handleDiscard}
      />
      <FinishBedAssignmentConfirmationModal
        open={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        onConfirm={handleMonitorBedAssociations}
      />
      <ModalContainer
        modalHidden={!isOpen}
        loading={isLoading}
        onClose={() => {
          if (!isEqual(beds.data, tempBeds) || !isEqual(patientMonitors.data, tempPatientMonitors))
            setShowUnsavedModal(true);
          else {
            onClose(true);
            setStep(1);
          }
        }}
        headerTitle={t('BedManagementModal.title')}
        headerIcon={<BedIcon />}
        footer={
          step === 1 ? (
            <Button
              variant='contained'
              fullWidth
              disabled={isDisabled || tempBeds?.length === 0}
              onClick={() => void handleNext()}
              data-testid='next-assign-beds'
            >
              {t('BedManagementModal.firstStepConfirmButton')}
            </Button>
          ) : (
            <Grid container display='flex' flexDirection='row' justifyContent='space-between'>
              <BedManagementHalfTextButton
                variant='outlined'
                sx={{ width: '49%' }}
                disabled={beds.data?.length === 0 || Object.values(errors).some((error) => !!error)}
                onClick={handleBack}
                data-testid='back-add-beds'
              >
                {t('BedManagementModal.secondStepGoBackButton')}
              </BedManagementHalfTextButton>
              <BedManagementHalfTextButton
                variant='contained'
                sx={{ width: '49%' }}
                disabled={
                  !tempPatientMonitors.find((pm: PatientMonitor) => pm.assignedBedId !== null)
                }
                onClick={handleFinishSetup}
                data-testid='finish-bed-setup'
              >
                {t('BedManagementModal.secondStepConfirmButton')}
              </BedManagementHalfTextButton>
            </Grid>
          )
        }
      >
        {step === 1 ? (
          <AddBedsContent
            beds={tempBeds}
            errors={errors}
            onAddBed={addTempBed}
            onModifyBedNo={modifyTempBedNo}
            onRemoveBed={removeTempBed}
            serverError={serverError}
            onChangeBedNo={changeBedNo}
          />
        ) : (
          <AssignBedContent
            beds={tempBeds}
            patientMonitors={tempPatientMonitors}
            onAdd={setTempPatientMonitors}
            isLoading={patientMonitors.isLoading}
            serverError={serverError}
          />
        )}
      </ModalContainer>
    </>
  );
};

export default BedManagementModal;
