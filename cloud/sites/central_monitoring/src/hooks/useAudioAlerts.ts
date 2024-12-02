import { VitalsAlert } from '@/types/alerts';
import { AUDIO_ALERT_CODES } from '@/utils/metricCodes';
import { useMemo } from 'react';

/**
 * Calculates and memoizes the audio alerts from the vitals alerts
 * @param vitalsAlerts List of current vitals alerts
 */
const useAudioAlerts = (vitalsAlerts: VitalsAlert[]): VitalsAlert[] =>
  useMemo(
    () =>
      vitalsAlerts.filter((vitalAlert: VitalsAlert) =>
        Object.values(AUDIO_ALERT_CODES).find(({ code }) => code === vitalAlert.code)
      ),
    [vitalsAlerts]
  );

export default useAudioAlerts;
