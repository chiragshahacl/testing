import { useBeds } from '@/api/useBeds';
import { useGroups } from '@/api/useGroups';
import usePatientData from '@/hooks/usePatientsData';
import { MockBeds, MockGroups } from '@/utils/groupsMockData';
import { useState } from 'react';

const TestComponent = () => {
  const {
    activeGroupId,
    updateSelectedBed,
    resetPatientsContext,
    removeSelfFromBedsDisplayGroup,
    updateBedsOnDisplay,
    updateActiveGroup,
    getGroupById,
    getActiveGroup,
    selectedBed,
  } = usePatientData();
  const [fetchedGroup, setFetchedGroup] = useState<string>();
  const [fetchedBed, setFetchedBed] = useState<string>();
  const bedGroups = useGroups();
  const beds = useBeds();

  const fetchGroupById = () => {
    const group = getGroupById(MockGroups[3].id);
    setFetchedGroup(JSON.stringify(group));
  };

  const fetchActiveGroup = () => {
    const group = getActiveGroup();
    setFetchedGroup(JSON.stringify(group));
  };

  return (
    <>
      <p>activeGroupId: {activeGroupId}</p>
      <button onClick={() => updateSelectedBed('bed_3')}>updateSelectedBed</button>
      <button onClick={resetPatientsContext}>resetPatientsContext</button>
      <button onClick={removeSelfFromBedsDisplayGroup}>removeSelfFromBedsDisplayGroup</button>
      <button onClick={() => updateBedsOnDisplay([MockBeds[0]])}>updateBedsOnDisplay</button>
      <button onClick={() => updateActiveGroup(MockGroups[2].id)}>updateActiveGroup</button>
      <p>groups count: {bedGroups?.data?.length}</p>
      <p>fetchedGroup: {fetchedGroup}</p>
      <button onClick={fetchGroupById}>getGroupById</button>
      <p>beds count: {beds?.data?.length}</p>
      <p>fetchedBed: {JSON.stringify(selectedBed)}</p>
      <p>activeGroup: {fetchedGroup}</p>
      <button onClick={fetchActiveGroup}>getActiveGroup</button>
    </>
  );
};

export default TestComponent;
