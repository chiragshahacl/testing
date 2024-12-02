import Loading from '@/app/loading';
import BedIcon from '@/components/icons/BedIcon';
import PatientMonitorIcon from '@/components/icons/PatientMonitorIcon';
import { NO_ASSIGNED_VALUE } from '@/constants';
import { Content, ContentHeader, ModalContentScrollContainer } from '@/styles/StyledComponents';
import { BedType } from '@/types/bed';
import { PatientMonitor } from '@/types/patientMonitor';
import FormControl from '@mui/material/FormControl';
import Grid from '@mui/material/Grid';
import MenuItem from '@mui/material/MenuItem';
import { PopoverOrigin } from '@mui/material/Popover';
import Select from '@mui/material/Select';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';
import { cloneDeep } from 'lodash';
import { useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { styled } from '@mui/material';

interface AssignBedContentProps {
  beds: BedType[];
  patientMonitors: PatientMonitor[];
  onAdd: (patientMonitors: PatientMonitor[]) => void;
  serverError: string | null;
  isLoading: boolean;
}

const AssignBedTable = styled(Table)(() => ({
  marginRight: '16px',
}));

const AssignBedContent = ({
  beds,
  patientMonitors,
  onAdd,
  serverError,
  isLoading,
}: AssignBedContentProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [anchorOrigin, setAnchorOrigin] = useState<PopoverOrigin>({
    vertical: 'top',
    horizontal: 'left',
  });

  const { t } = useTranslation();
  const assignBed = (index: number, bedID: string) => {
    const newAssignments = cloneDeep(patientMonitors);
    if (index >= 0) {
      newAssignments[index].assignedBedId = bedID;
      onAdd(newAssignments);
    }
  };

  const positionDropdown = (dropdownRef: Element | null = null) => {
    const containerBoundary = containerRef?.current?.getBoundingClientRect();
    const selectMenuBoundaryBottom = dropdownRef?.getBoundingClientRect().bottom;

    if (containerBoundary?.bottom && selectMenuBoundaryBottom) {
      if (containerBoundary.bottom <= selectMenuBoundaryBottom + 231) {
        setAnchorOrigin({
          vertical: 'bottom',
          horizontal: 'left',
        });
      } else if (containerBoundary.bottom > selectMenuBoundaryBottom + 231) {
        setAnchorOrigin({
          vertical: 'top',
          horizontal: 'left',
        });
      }
    }
  };

  return (
    <Content style={{ flex: 2, paddingRight: 0 }}>
      <ContentHeader>
        <Grid display='flex' flexDirection='column' sx={{ flex: 1 }}>
          <Typography variant='h2' sx={{ mb: 8 }} data-testid='assign-beds-title'>
            {t('BedManagementModal.secondStepTitle')}
          </Typography>
          <Typography variant='caption'>Select the bed ID in the second column.</Typography>
          <Typography variant='h5' color='error.secondary' data-testid='assign-beds-error'>
            {serverError}
          </Typography>
        </Grid>
      </ContentHeader>
      <ModalContentScrollContainer
        ref={containerRef}
        container
        display='flex'
        alignItems='flex-start'
      >
        {isLoading ? (
          <Loading height='100%' />
        ) : (
          <AssignBedTable>
            <TableHead>
              <TableRow sx={{ borderBottom: (theme) => `2px solid ${theme.palette.divider}` }}>
                <TableCell
                  sx={{
                    width: '30%',
                  }}
                >
                  <Grid
                    container
                    display='flex'
                    flexDirection='row'
                    alignItems='center'
                    sx={{ gap: 9 }}
                  >
                    <PatientMonitorIcon />
                    <Typography variant='h5'>
                      {t('BedManagementModal.secondStepMonitorIdLabel')}
                    </Typography>
                  </Grid>
                </TableCell>
                <TableCell
                  sx={{
                    width: '70%',
                  }}
                >
                  <Grid
                    container
                    display='flex'
                    flexDirection='row'
                    alignItems='center'
                    sx={{ gap: 9 }}
                  >
                    <BedIcon />
                    <Typography variant='h5'>Bed ID</Typography>
                  </Grid>
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {patientMonitors
                .sort((a, b) =>
                  a.monitorId.toLowerCase() > b.monitorId.toLowerCase()
                    ? 1
                    : b.monitorId.toLowerCase() > a.monitorId.toLowerCase()
                    ? -1
                    : 0
                )
                .map((patientMonitor: PatientMonitor, index: number) => (
                  <TableRow key={patientMonitor.id}>
                    <TableCell sx={{ padding: (theme) => theme.spacing(2, 2, 2, 16) }}>
                      <Typography variant='body1'>{patientMonitor.monitorId}</Typography>
                    </TableCell>
                    <TableCell sx={{ padding: (theme) => theme.spacing(2, 16, 2, 2) }}>
                      <FormControl sx={{ width: 260 }} size='small'>
                        <Select
                          data-testid={`select-${index}`}
                          sx={{
                            boxShadow: 'none',
                            '.MuiOutlinedInput-notchedOutline': { border: 0 },
                            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                              border: 0,
                            },
                          }}
                          onOpen={(e) => positionDropdown(e.currentTarget)}
                          value={patientMonitor?.assignedBedId || NO_ASSIGNED_VALUE}
                          onChange={(e) => assignBed(index, e.target.value)}
                          MenuProps={{
                            anchorOrigin: anchorOrigin,
                            transformOrigin: anchorOrigin,
                            PaperProps: {
                              sx: {
                                backgroundImage: 'none',
                                backgroundColor: 'transparent',
                              },
                            },
                            MenuListProps: {
                              sx: {
                                backgroundColor: 'secondary.main',
                                border: '4px solid #1A5F89',
                                borderRadius: 16,
                                padding: 0,
                                maxHeight: 231,
                                overflowY: 'scroll',
                                overflowX: 'hidden',
                                '::-webkit-scrollbar': {
                                  width: '4px',
                                },
                                '::-webkit-scrollbar-thumb': {
                                  backgroundColor: '#D0D3D7',
                                  borderRadius: '16px',
                                },
                                '::-webkit-scrollbar-track': {
                                  backgroundColor: 'transparent',
                                },
                              },
                            },
                          }}
                        >
                          <MenuItem value={NO_ASSIGNED_VALUE}>
                            <Typography variant='body1'>N/A</Typography>
                          </MenuItem>
                          {beds
                            .sort((a, b) =>
                              a.bedNo.toLowerCase() > b.bedNo.toLowerCase()
                                ? 1
                                : b.bedNo.toLowerCase() > a.bedNo.toLowerCase()
                                ? -1
                                : 0
                            )
                            .map((bed: BedType, bedIndex: number) => (
                              <MenuItem
                                data-testid={`select-option-${bedIndex}`}
                                key={bed.id}
                                value={bed.id}
                                disabled={
                                  bed.id !== patientMonitor.assignedBedId &&
                                  patientMonitors.map((pm) => pm.assignedBedId).includes(bed.id)
                                }
                                selected={bed.id === patientMonitor.assignedBedId}
                              >
                                <Typography variant='body1'>{bed.bedNo}</Typography>
                              </MenuItem>
                            ))}
                        </Select>
                      </FormControl>
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </AssignBedTable>
        )}
      </ModalContentScrollContainer>
    </Content>
  );
};

export default AssignBedContent;
