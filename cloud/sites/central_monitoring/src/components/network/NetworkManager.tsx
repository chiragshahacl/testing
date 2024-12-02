'use client';

import { useHealthcheck } from '@/api/useHealthcheck';
import NetworkStatusModal from '@/components/modals/NetworkStatusModal';
import useAudioManager from '@/hooks/useAudioManager';
import useNetwork from '@/hooks/useNetwork';
import { generateLostConnectionAlert } from '@/utils/alertUtils';
import { useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';

const NetworkManager = (): JSX.Element => {
  const queryClient = useQueryClient();
  const networkIsOnline = useNetwork();
  const serverIsOnline = useHealthcheck();
  const { setAudioAlert, setActiveAlertsExist } = useAudioManager();

  const onLostConnection = useCallback(() => {
    setAudioAlert([generateLostConnectionAlert(networkIsOnline)], true);
    setActiveAlertsExist(true);
  }, [networkIsOnline, setAudioAlert]);

  const onConfirm = useCallback(() => {
    void queryClient.resetQueries();
  }, [queryClient]);

  return (
    <>
      <NetworkStatusModal
        isOnline={networkIsOnline}
        onLostConnection={onLostConnection}
        onConfirm={onConfirm}
        title='Network disconnected'
        description='Unable to detect a network connection. Please check your network settings. If the problem persists, contact support.'
      />
      <NetworkStatusModal
        isOnline={serverIsOnline}
        onLostConnection={onLostConnection}
        onConfirm={onConfirm}
        title='Something went wrong'
        description='The system has detected an error during operation. If the problem persists, contact support and restart the central server.'
      />
    </>
  );
};

export default NetworkManager;
