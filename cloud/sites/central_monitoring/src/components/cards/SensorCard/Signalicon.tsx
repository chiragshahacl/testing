import {
  FairSignalIcon,
  GoodSignalIcon,
  NoSignalIcon,
  WeakSignalIcon,
} from '@/components/icons/connectionSignal';

export enum SIGNAL_LEVEL {
  NO_SIGNAL = -100,
  WEAK_SIGNAL = -93,
  FAIR_SIGNAL = -76,
}

interface SignalIconProps {
  signal: SIGNAL_LEVEL;
}

export const SignalIcon = ({ signal }: SignalIconProps) => {
  if (signal === SIGNAL_LEVEL.NO_SIGNAL) {
    return <NoSignalIcon />;
  } else if (signal <= SIGNAL_LEVEL.WEAK_SIGNAL) {
    return <WeakSignalIcon />;
  } else if (signal <= SIGNAL_LEVEL.FAIR_SIGNAL) {
    return <FairSignalIcon />;
  } else {
    return <GoodSignalIcon />;
  }
};
