import EHRAdmitSelectionSection from './components/EHRAdmitSelectionSection';
import { EHRStep } from '@/utils/ehr';

interface EHRAdmitSelectionProps {
  updateEHRState: (newState: EHRStep) => void;
}

const EHRAdmitSelection = ({ updateEHRState }: EHRAdmitSelectionProps) => {
  const onSearchAdmitClick = () => {
    updateEHRState(EHRStep.SEARCH);
  };

  const onQuickAdmitClick = () => {
    updateEHRState(EHRStep.QUICK_ADMIT);
  };

  return (
    <>
      <EHRAdmitSelectionSection
        buttonText={'Search'}
        titleText={'Admit and Monitor Patient'}
        onButtonClick={onSearchAdmitClick}
      />
      <EHRAdmitSelectionSection
        buttonText={'Quick admit'}
        titleText={'Quick Admit New Patient - Anne One'}
        onButtonClick={onQuickAdmitClick}
      />
    </>
  );
};

export default EHRAdmitSelection;
