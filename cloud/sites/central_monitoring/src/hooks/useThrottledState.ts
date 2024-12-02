import { isFunction, throttle } from 'lodash';
import { Dispatch, SetStateAction, useRef, useState } from 'react';

/**
 * Works same as the `React.useState` hook, but throttles the update of state
 * so that the render is not triggered too many times for fast changing data.
 *
 * @param initialState
 * @param rateLimit It will not trigger the state update more than once every `rateLimit` milliseconds.
 */
function useThrottledState<T>(
  initialState: T,
  rateLimit: number
): [T, Dispatch<SetStateAction<T>>] {
  const [state, setInternalState] = useState<T>(initialState);
  const stateReference = useRef<T>(initialState);

  const throttledSetInternalState = throttle(
    () => setInternalState(stateReference.current),
    rateLimit,
    { trailing: true, leading: false }
  );

  const setState: Dispatch<SetStateAction<T>> = (setStateAction) => {
    if (isFunction(setStateAction)) {
      stateReference.current = setStateAction(stateReference.current);
    } else {
      stateReference.current = setStateAction;
    }
    throttledSetInternalState();
  };

  return [state, setState];
}

export default useThrottledState;
