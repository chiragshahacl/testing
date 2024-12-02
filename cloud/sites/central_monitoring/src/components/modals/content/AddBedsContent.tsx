import AddIcon from '@/components/icons/AddIcon';
import RemoveIcon from '@/components/icons/RemoveIcon';
import { bedManagementErrors } from '@/constants';
import { Content, ContentHeader, ModalContentScrollContainer } from '@/styles/StyledComponents';
import { BedType } from '@/types/bed';
import { styled } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import MaxValueReachedModal from '../MaxValueReachedModal';
import { getCachedRuntimeConfig } from '@/utils/runtime';

const customErrorColor = '#FF8585';

const BedTextField = styled(TextField)(({ theme }) => ({
  width: 488,
  height: 56,
  '.MuiInputBase-input.Mui-disabled': {
    borderColor: theme.palette.common.white,
  },
  '.MuiInputBase-input.Mui-error': {
    color: customErrorColor,
  },
  '.MuiInputBase-input': {
    borderColor: theme.palette.common.white,
  },
}));

interface AddBedsContentProps {
  beds: BedType[];
  errors: Record<string, string | undefined>;
  serverError: string | null;
  onAddBed: () => void;
  onModifyBedNo: (bedId: string, newBedNo: string) => void;
  onRemoveBed: (bedId: string) => void;
  onChangeBedNo: (bedId: string, bedNo: string) => void;
}

const AddBedsContent = ({
  beds,
  errors,
  serverError,
  onAddBed,
  onModifyBedNo,
  onRemoveBed,
  onChangeBedNo,
}: AddBedsContentProps) => {
  const [showMaxBedsModal, setShowMaxBedsModal] = useState<boolean>(false);
  const { t } = useTranslation();
  const MAX_NUMBER_BEDS = parseInt(getCachedRuntimeConfig().MAX_NUMBER_BEDS);

  const handleAddBed = () => {
    if (beds.length < MAX_NUMBER_BEDS) {
      onAddBed();
    } else {
      setShowMaxBedsModal(true);
    }
  };

  return (
    <>
      <MaxValueReachedModal
        open={showMaxBedsModal}
        handleClose={() => setShowMaxBedsModal(false)}
      />
      <Content style={{ flex: 2 }}>
        <ContentHeader>
          <Grid
            display='flex'
            flexDirection='row'
            justifyContent='space-between'
            alignItems='center'
            sx={{ flex: 1 }}
          >
            <Typography variant='body3' data-testid='add-beds-title'>
              {t('BedManagementModal.firstStepTitle', { count: beds.length })}
            </Typography>
            {serverError !== bedManagementErrors['failedToFetch'] && (
              <Box data-testid='add-bed' sx={{ mr: 7 }} onClick={handleAddBed}>
                <AddIcon />
              </Box>
            )}
          </Grid>
        </ContentHeader>
        <ModalContentScrollContainer container display='flex'>
          {serverError ? (
            <Typography variant='h5' color='error.secondary' data-testid='add-beds-error'>
              {serverError}
            </Typography>
          ) : (
            <>
              {beds.length === 0 ? (
                <Typography variant='caption' sx={{ paddingX: 16 }} data-testid='no-beds-text'>
                  {t('BedManagementModal.firstStepInstructionText')}
                </Typography>
              ) : (
                <Grid item display='flex' flexDirection='column' sx={{ gap: 8, marginLeft: '6px' }}>
                  {beds.map((bed: BedType, index: number) => (
                    <Grid
                      key={bed.id}
                      item
                      display='flex'
                      flexDirection='row'
                      alignItems='center'
                      sx={{ gap: 36 }}
                    >
                      <Typography variant='body3'>
                        {t('BedManagementModal.firstStepBedIdLabel')}
                      </Typography>
                      <Grid item display='flex' flexDirection='column'>
                        <BedTextField
                          error={!!errors[bed.id]}
                          sx={{
                            '& fieldset': {
                              borderColor: errors[bed.id]
                                ? `${customErrorColor} !important`
                                : '#F2F4F6 !important',
                            },
                          }}
                          inputProps={{
                            'aria-label': bed.bedNo,
                            'data-testid': `bed-edit-${index + 1}`,
                          }}
                          defaultValue={bed.bedNo}
                          onChange={(e) => onChangeBedNo(bed.id, e.target.value.trim())}
                          onBlur={(e) => onModifyBedNo(bed.id, e.target.value.trim())}
                          autoFocus={index === beds.length - 1}
                        />
                        {errors[bed.id] && (
                          <Typography
                            variant='error'
                            sx={{
                              color: customErrorColor,
                              lineHeight: '24.51px',
                              marginLeft: '12px',
                              marginTop: '8px',
                            }}
                          >
                            {errors[bed.id]}
                          </Typography>
                        )}
                      </Grid>
                      <Box
                        data-testid={`remove-bed-${index + 1}`}
                        onClick={() => onRemoveBed(bed.id)}
                      >
                        <RemoveIcon />
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              )}
            </>
          )}
        </ModalContentScrollContainer>
      </Content>
    </>
  );
};

export default AddBedsContent;
