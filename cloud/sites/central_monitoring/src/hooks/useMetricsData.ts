import { MetricsData } from '@/context/MetricsContext';
import { useContext } from 'react';

/**
 * @description Hook for accesing content from the MetricsData Context safely
 * @returns Context for MetricsData
 */
const useMetricsData = () => {
  const context = useContext(MetricsData);

  if (context === null) {
    throw new Error('useMetricsData must be used within a MetricsProvider');
  }

  return context;
};

export default useMetricsData;
