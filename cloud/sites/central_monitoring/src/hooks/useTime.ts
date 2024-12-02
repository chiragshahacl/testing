import { PatientsData } from '@/context/PatientsContext';
import moment from 'moment';
import { useContext, useEffect, useState } from 'react';
import { getCachedRuntimeConfig } from '../utils/runtime';

const TIME_INTERVAL = 20000;

/**
 * @description Custom hook for managing and providing the current date/time based on hospital timezone.
 * @returns {object} The current date/time.
 */
const useTime = () => {
  const context = useContext(PatientsData);
  const [currentDate, setCurrentDate] = useState(moment());

  useEffect(() => {
    setCurrentDate(moment().tz(getCachedRuntimeConfig().HOSPITAL_TZ ?? 'UTC'));

    const interval = setInterval(() => {
      setCurrentDate(moment().tz(getCachedRuntimeConfig().HOSPITAL_TZ ?? 'UTC'));
      if (context !== null) context.bedsDisplayGroupsKeepAlive();
    }, TIME_INTERVAL);
    return () => {
      clearInterval(interval);
    };
  }, [context]);

  return currentDate;
};

export default useTime;
