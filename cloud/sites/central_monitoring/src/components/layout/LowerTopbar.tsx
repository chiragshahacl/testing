'use client';

import { useGroups } from '@/api/useGroups';
import GroupMngmntIcon from '@/components/icons/GroupMngmntIcon';
import SettingsIcon from '@/components/icons/SettingsIcon';
import { ALERT_AUDIO } from '@/constants';
import useAudioManager from '@/hooks/useAudioManager';
import usePatientData from '@/hooks/usePatientsData';
import { STORAGE_KEYS } from '@/utils/storage';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import moment from 'moment';
import Image from 'next/image';
import { useCallback, useEffect, useRef } from 'react';
import AudioOff from '../icons/AudioOff';
import AudioOn from '../icons/AudioOn';
import AudioPaused from '../icons/AudioPaused';
import BedIcon from '../icons/BedIcon';
import HorizontalList from '../lists/HorizontalList';

interface LowerTopbarProps {
  settingsOnly?: boolean;
  setShowSettings?: (value: boolean) => void;
  showSettings?: boolean;
  customUpdateGroup?: (value: string) => void;
}

const LowerTopbar = ({
  settingsOnly = false,
  setShowSettings = () => undefined,
  showSettings = false,
  customUpdateGroup = undefined,
}: LowerTopbarProps) => {
  const bedGroups = useGroups();
  const {
    audioAlarmSetting,
    audioIsActive,
    setAudioIsActive,
    audioDisabledTimer,
    setAudioDisabledTimer,
    timerIsPaused,
  } = useAudioManager();
  const { activeGroupId, updateActiveGroup, setBedManagementModal, setGroupManagementModal } =
    usePatientData();
  const timer = useRef<NodeJS.Timer | undefined>(undefined);

  const handleUpdateGroup = (groupId: string) => {
    if (customUpdateGroup) {
      customUpdateGroup(groupId);
    } else {
      updateActiveGroup(groupId);
    }
  };

  const handleAudioOnChange = useCallback(
    (checked: boolean) => {
      localStorage.setItem(STORAGE_KEYS.ALERT_AUDIO_PAUSED, checked.toString());
      setAudioIsActive(checked);
    },
    [setAudioIsActive]
  );

  useEffect(() => {
    // Sets interval for audio pause countdown
    if (!audioIsActive) {
      timer.current = setInterval(() => {
        if (!timerIsPaused) {
          setAudioDisabledTimer((prevRemainingTime: number) => {
            const updatedRemainingTime = prevRemainingTime - 1;
            if (updatedRemainingTime < 0) {
              handleAudioOnChange(true);
            }
            return updatedRemainingTime;
          });
        }
      }, 1000);
    }

    return () => {
      if (timer.current) clearInterval(timer.current);
    };
  }, [audioIsActive, handleAudioOnChange, setAudioDisabledTimer, timerIsPaused]);

  return (
    <>
      <Grid
        item
        container
        direction='row'
        justifyContent='space-between'
        alignItems='center'
        sx={{
          backgroundColor: 'secondary.main',
          paddingX: 16,
        }}
      >
        <Grid item display='flex' alignItems='center'>
          <Image
            src='/topbarLogo.png'
            height={42}
            width={80}
            alt={'anne-stream-logo'}
            style={{ marginRight: 5 }}
            priority
          />
          {!settingsOnly && (
            <Grid
              display='flex'
              sx={{
                width: 'calc(100vw * 0.34)',
              }}
            >
              <HorizontalList
                items={bedGroups?.data || []}
                activeItem={activeGroupId}
                setActiveItem={handleUpdateGroup}
              />
            </Grid>
          )}
        </Grid>
        <Grid item display='flex' height={48}>
          {!settingsOnly && (
            <>
              {audioAlarmSetting !== ALERT_AUDIO.OFF ? (
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'center',
                    flexDirection: 'row',
                    alignItems: 'center',
                  }}
                >
                  {audioIsActive ? <AudioOn /> : <AudioPaused />}
                  <Typography variant='body2' ml={5}>
                    {audioIsActive
                      ? 'Central Audio on'
                      : `Central Audio Paused ${moment
                          .utc(moment.duration(audioDisabledTimer, 'seconds').asMilliseconds())
                          .format('mm:ss')}`}
                  </Typography>
                  <Button
                    size='small'
                    variant='contained'
                    sx={{
                      whiteSpace: 'nowrap',
                      minWidth: 'auto',
                      backgroundColor: audioIsActive ? 'primary.light' : 'common.white',
                      '&:hover': {
                        backgroundColor: audioIsActive ? 'primary.light' : 'common.white',
                      },
                    }}
                    onClick={() => handleAudioOnChange(!audioIsActive)}
                  >
                    {audioIsActive ? 'Pause' : 'Cancel'}
                  </Button>
                </Box>
              ) : (
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'center',
                    flexDirection: 'row',
                    alignItems: 'center',
                    backgroundColor: 'common.white',
                    padding: (theme) => theme.spacing(4, 8),
                    gap: 8,
                    borderRadius: 8,
                    my: 6,
                  }}
                >
                  <AudioOff />
                  <Typography variant='body2' color='common.black'>
                    Central Audio Off
                  </Typography>
                </Box>
              )}
              <Box
                height={23.5}
                width='1px'
                marginX={20}
                sx={{
                  backgroundColor: 'background.inactive',
                  display: 'flex',
                  alignSelf: 'center',
                }}
              />
              <Button variant='text' onClick={() => setBedManagementModal(true)}>
                <BedIcon />
                <Typography variant='body2'>Bed Management</Typography>
              </Button>
              <Button variant='text' sx={{ mr: 15 }} onClick={() => setGroupManagementModal(true)}>
                <GroupMngmntIcon />
                <Typography variant='body2'>Group Management</Typography>
              </Button>
            </>
          )}
          <Button
            variant='text'
            sx={{ backgroundColor: showSettings ? 'background.modal' : null }}
            onClick={() => setShowSettings(!showSettings)}
          >
            <SettingsIcon />
            <Typography variant='body2'>Settings</Typography>
          </Button>
        </Grid>
      </Grid>
      <Box className='topbar-border' />
    </>
  );
};

export default LowerTopbar;
