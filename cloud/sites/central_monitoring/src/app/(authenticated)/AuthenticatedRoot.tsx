'use client';

import { useBeds } from '@/api/useBeds';
import { useGroups } from '@/api/useGroups';
import { useHealthcheck } from '@/api/useHealthcheck';
import Loading from '@/app/loading';
import SettingsSidebar from '@/components/Settings/Sidebar';
import LowerTopbar from '@/components/layout/LowerTopbar';
import SystemStatusBar from '@/components/layout/SystemStatusBar';
import AlertEnabledModal from '@/components/modals/AlertEnabledModal';
import BedManagementModal from '@/components/modals/BedManagementModal';
import GroupManagementModal from '@/components/modals/GroupManagementModal';
import NetworkManager from '@/components/network/NetworkManager';
import { USER_TYPE } from '@/constants';
import useAudioManager from '@/hooks/useAudioManager';
import useNetwork from '@/hooks/useNetwork';
import usePatientData from '@/hooks/usePatientsData';
import useSession from '@/hooks/useSession';
import Grid from '@mui/material/Grid';
import { useRouter } from 'next/navigation';
import React, { useEffect, useMemo, useState } from 'react';

interface AuthenticatedRootProps {
  children: React.ReactNode;
}

const AuthenticatedRoot = ({ children }: AuthenticatedRootProps) => {
  const router = useRouter();
  const [showSettings, setShowSettings] = useState<boolean>(false);

  const { accessToken, refreshToken, authenticating, userType } = useSession();
  const { setAutoPlayActivated } = useAudioManager();
  const {
    updateActiveGroup,
    setBedManagementModal,
    bedManagementModalIsOpen,
    setGroupManagementModal,
    groupManagementModalIsOpen,
  } = usePatientData();
  const beds = useBeds();
  const bedGroups = useGroups();
  const networkIsOnline = useNetwork();
  const serverIsOnline = useHealthcheck();

  useEffect(() => {
    // Redirects to login if not authenticated
    if (!authenticating && !(accessToken && refreshToken && userType == USER_TYPE.NON_TECH)) {
      router.replace('/login');
    }
  }, [accessToken, authenticating, refreshToken, router, userType]);

  const showMainComponents = useMemo(
    () =>
      networkIsOnline && serverIsOnline && !bedManagementModalIsOpen && !groupManagementModalIsOpen,
    [networkIsOnline, serverIsOnline, bedManagementModalIsOpen, groupManagementModalIsOpen]
  );

  if (accessToken && refreshToken && userType == USER_TYPE.NON_TECH)
    return (
      <Grid display='flex' flexDirection='column' height='-webkit-fill-available'>
        <NetworkManager />
        <AlertEnabledModal />
        <SystemStatusBar />
        {groupManagementModalIsOpen && (
          <GroupManagementModal
            isOpen={groupManagementModalIsOpen}
            onClose={() => {
              setGroupManagementModal(false);
            }}
          />
        )}
        {bedManagementModalIsOpen && (
          <BedManagementModal
            isOpen={bedManagementModalIsOpen}
            onClose={(closeAllModals) => {
              setAutoPlayActivated(true); // Enable the audio as the user interacted with the page to close the modal
              setBedManagementModal(false);
              if (closeAllModals) {
                setGroupManagementModal(false);
              }
            }}
          />
        )}
        <LowerTopbar
          settingsOnly={beds.isLoading || bedGroups.isLoading}
          showSettings={showSettings}
          setShowSettings={setShowSettings}
          customUpdateGroup={updateActiveGroup}
        />
        {
          <Grid display={showMainComponents ? 'flex' : 'none'} flexDirection='row' flex={1}>
            <Grid sx={{ width: showSettings ? '74%' : '100%' }}>{children}</Grid>
            <Grid
              container
              display={showSettings ? 'flex' : 'none'}
              flexDirection='row'
              sx={{ width: '26%' }}
              data-testid='settings-component'
            >
              <SettingsSidebar />
            </Grid>
          </Grid>
        }
      </Grid>
    );
  return <Loading />;
};

export default AuthenticatedRoot;
