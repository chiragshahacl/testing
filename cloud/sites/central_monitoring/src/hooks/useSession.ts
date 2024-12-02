import { Session } from '@/context/SessionContext';
import { useContext } from 'react';

/**
 * @description Hook for accesing content from the Session Context safely
 * @returns Context for Session
 */
const useSession = () => {
  const context = useContext(Session);

  if (context === null) {
    throw new Error('useSession must be used within a SessionProvider');
  }

  return context;
};

export default useSession;
