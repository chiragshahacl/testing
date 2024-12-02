import { debounce } from 'lodash';
import { useCallback, useEffect } from 'react';

/**
 * @description Debounce a function call to prevent it from being called too often.
 * It will be called after the delay has passed with the last arguments passed to the wrapper function.
 * @param callback The function to debounce.
 * @param delay The delay in milliseconds.
 * @returns The debounced function.
 */
function useDebounce(callback: () => void, delay: number) {
  const debouncedCallback = useCallback(debounce(callback, delay), [delay]);

  useEffect(() => {
    return () => {
      debouncedCallback.cancel();
    };
  }, [delay, debouncedCallback]);

  return debouncedCallback;
}

export default useDebounce;
