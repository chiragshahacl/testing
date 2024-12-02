'use client';

import { AudioManager } from '@/context/AudioManagerContext';
import { useContext } from 'react';

/**
 * @description Hook for accesing content from the AudioManager Context safely
 * @returns Context for AudioManager
 */
const useAudioManager = () => {
  const context = useContext(AudioManager);

  if (context === null) {
    throw new Error('useAudioManager must be used within a AudioManagerProvider');
  }

  return context;
};

export default useAudioManager;
