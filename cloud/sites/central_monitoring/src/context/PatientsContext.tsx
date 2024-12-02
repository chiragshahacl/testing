import { useBeds } from '@/api/useBeds';
import { useGroups } from '@/api/useGroups';
import { usePatientMonitors } from '@/api/usePatientMonitors';
import useTypedSearchParams from '@/hooks/useTypedSearchParams';
import { BedType } from '@/types/bed';
import { GroupType } from '@/types/group';
import { BedsDisplayGroup } from '@/types/patientMonitor';
import { getStoredDisplayedBeds, saveStoredDisplayedBeds } from '@/utils/storage';
import { cloneDeep } from 'lodash';
import moment from 'moment';
import {
  MutableRefObject,
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import { v4 as uuidv4 } from 'uuid';

interface PatientContextProps {
  children: React.ReactNode;
}

interface PatientsContextType {
  getGroupById: (groupId: string) => GroupType | undefined;
  getActiveGroup: () => GroupType | typeof EMPTY_GROUP;
  selectedBed: BedType | undefined;
  updateActiveGroup: (newGroup: string) => void;
  activeGroupId: string;
  loadingSelectedBed: boolean;
  updateSelectedBed: (bedId: string) => void;
  setBedManagementModal: (value: boolean) => void;
  bedManagementModalIsOpen: boolean;
  resetPatientsContext: () => void;
  bedsDisplayGroups: BedsDisplayGroup[];
  updateBedsOnDisplay: (newBeds: BedType[]) => void;
  bedsDisplayGroupsKeepAlive: () => void;
  removeSelfFromBedsDisplayGroup: () => void;
  groupManagementModalIsOpen: boolean;
  setGroupManagementModal: (value: boolean) => void;
  monitorsFreshDataKeepAlive: MutableRefObject<Record<string, number>>;
  resetMonitorsKeepAlive: () => void;
  updateKeepAlive: (monitorId: string) => void;
}

export const PatientsData = createContext<PatientsContextType | null>(null);

const DEFAULT_ACTIVE_GROUP = '';

const EMPTY_GROUP: GroupType = { id: '', name: '', beds: [] };
const SCREEN_ID = uuidv4();
const DISPLAY_GROUPS_EXPIRY_TIME = 30000;

/**
 * @description Manages selected beds and groups, and status of modals relating to them.
 *      Also manages status of shown beds, both for monitor keep alives and display warnings
 * @returns Values included are:
 * activeGroupId - String. Id of the currently selected Group
 * getActiveGroup - Method for fetching the currently selected Group
 * getGroupById - Method for fetching a specific group by Id
 * updateActiveGroup - Method for updating which group is currently selected
 *
 * selectedBed - BedType. Bed data for the currently selected Bed
 * updateSelectedBed - Method for updating which bed is currently selected
 * loadingSelectedBed - Boolean. Indicates if CMS is loading the currently selected bed
 *
 * bedManagementModalIsOpen - Boolean. Indicates if BedManagementModal should be open
 * setBedManagementModal - Method for setting if the BedManagementModal should be open
 * groupManagementModalIsOpen - Boolean. Indicates if GroupManagementModal should be open
 * setGroupManagementModal - Method for setting if the GroupManagementModal should be open
 *
 * monitorsFreshDataKeepAlive - Record. Stores when was the last keep alive of each PM
 * updateKeepAlive - Method for updating the keep alive time of the received PM
 * resetMonitorsKeepAlive - Resets all current keep alive values for all PMs
 *
 * bedsDisplayGroups - BedsDisplayGroups[]. Information of which currently open CMS screens are
 *      showing which beds. To be used to ensure all PMs are being shown at the same time
 * updateBedsOnDisplay - Method for updating which beds are currently being shown on the current
 *      screen
 * bedsDisplayGroupsKeepAlive - Method for updating bedsDisplayGroups to renew the current screen
 *      timestamp, so we know current screen is still active
 * removeSelfFromBedsDisplayGroup - Method for removing current screen from bedsDisplayGroups. To
 *      be used when current screen is closed.
 *
 * resetPatientsContext - Method for resetting all data of the context to default.
 *
 */
const PatientsContext = ({ children }: PatientContextProps) => {
  const activeGroup = useRef<string>(DEFAULT_ACTIVE_GROUP);
  const searchParams = useTypedSearchParams();
  const [selectedBedId, setSelectedBedId] = useState<string | null>(null);
  const [bedManagementModalIsOpen, setBedManagementModal] = useState<boolean>(false);
  const [groupManagementModalIsOpen, setGroupManagementModal] = useState<boolean>(false);
  const [loadingSelectedBed, setLoadingSelectedBed] = useState<boolean>(false);
  const [bedsDisplayGroups, setBedsDisplayGroups] = useState<BedsDisplayGroup[]>([]);
  const monitorsFreshDataKeepAlive = useRef<Record<string, number>>({});

  const beds = useBeds();
  const patientMonitors = usePatientMonitors();
  const bedGroups = useGroups();

  const updateBedsOnDisplay = (newBeds: BedType[]) => {
    const newBedsIds: string[] = [];
    newBeds.forEach((bed) => {
      if (bed.id) {
        newBedsIds.push(bed.id);
      }
    });

    const newBedsOnDisplay = getStoredDisplayedBeds();

    const newBedGroup = {
      screenId: SCREEN_ID,
      beds: newBedsIds,
      timestamp: moment.now(),
    };
    const index = newBedsOnDisplay.findIndex((displayGroup) => {
      return displayGroup.screenId === SCREEN_ID;
    });
    if (index < 0) newBedsOnDisplay.push(newBedGroup);
    else newBedsOnDisplay[index] = newBedGroup;

    saveStoredDisplayedBeds(newBedsOnDisplay);
  };

  const updateActiveGroup = useCallback(
    (newGroup: string) => {
      if (bedGroups.data === undefined) return;
      const groupObject = bedGroups.data.find((groupBed: GroupType) => groupBed.id === newGroup);
      if (groupObject && groupObject.beds[0] && groupObject.beds[0].id) {
        updateBedsOnDisplay(groupObject.beds);
        updateSelectedBed(groupObject.beds[0].id);
      }

      activeGroup.current = newGroup;
    },
    [bedGroups.data]
  );

  const updateSelectedBed = (bedId: string) => {
    setLoadingSelectedBed(true);
    setSelectedBedId(bedId);
    setLoadingSelectedBed(false);
  };

  const getGroupById = useCallback(
    (groupId: string) => {
      return bedGroups?.data?.find((group: GroupType) => group.id === groupId);
    },
    [bedGroups?.data]
  );

  const getActiveGroup = useCallback((): GroupType | typeof EMPTY_GROUP => {
    if (!bedGroups?.data?.length) {
      return EMPTY_GROUP;
    } else if (!activeGroup.current && bedGroups.data && bedGroups.data.length > 0) {
      updateActiveGroup(bedGroups.data[0].id);
      return bedGroups.data[0];
    }
    return getGroupById(activeGroup.current) || EMPTY_GROUP;
  }, [bedGroups.data, getGroupById, updateActiveGroup]);

  const selectedBed = useMemo(
    () => beds?.data?.find((bed: BedType) => bed.id === selectedBedId),
    [beds?.data, selectedBedId]
  );

  const removeOutdatedBedsDisplayGroups = (originalBedsOnDisplay: BedsDisplayGroup[]) =>
    originalBedsOnDisplay.filter(
      (displayGroup) => displayGroup.timestamp + DISPLAY_GROUPS_EXPIRY_TIME >= moment.now()
    );

  const bedsDisplayGroupsKeepAlive = () => {
    const previousBedsOnDisplay = getStoredDisplayedBeds();
    const newBedsOnDisplay = previousBedsOnDisplay.map((displayGroup) => {
      if (displayGroup.screenId === SCREEN_ID) {
        return {
          ...displayGroup,
          timestamp: moment.now(),
        };
      } else return displayGroup;
    });
    const filteredBedsOnDisplay = removeOutdatedBedsDisplayGroups(newBedsOnDisplay);
    saveStoredDisplayedBeds(filteredBedsOnDisplay);
  };

  const removeSelfFromBedsDisplayGroup = () => {
    const newBedsDisplayGroups = cloneDeep(getStoredDisplayedBeds());
    const groupIndex = newBedsDisplayGroups.findIndex((displayGroup: BedsDisplayGroup) => {
      return displayGroup.screenId === SCREEN_ID;
    });
    newBedsDisplayGroups.splice(groupIndex, 1);
    saveStoredDisplayedBeds(newBedsDisplayGroups);
  };

  const resetPatientsContext = () => {
    activeGroup.current = DEFAULT_ACTIVE_GROUP;
    updateBedsOnDisplay([]);
    setSelectedBedId(null);
  };

  const resetMonitorsKeepAlive = () => {
    monitorsFreshDataKeepAlive.current = {};
  };

  const updateKeepAlive = (monitorId: string) => {
    monitorsFreshDataKeepAlive.current = {
      ...monitorsFreshDataKeepAlive.current,
      [monitorId]: Date.now(),
    };
  };

  useEffect(() => {
    // Coordinates which beds are displayed in all current CMS screens
    const storedBedsOnDisplay = getStoredDisplayedBeds();
    if (storedBedsOnDisplay) {
      setBedsDisplayGroups(storedBedsOnDisplay);
    }

    const handleSecureStorageChange = () => {
      const newBedsDisplayGroups = getStoredDisplayedBeds();
      setBedsDisplayGroups(newBedsDisplayGroups);
    };

    window.addEventListener('bedsDisplayGroupsUpdated', handleSecureStorageChange);

    return () => {
      window.removeEventListener('bedsDisplayGroupsUpdated', handleSecureStorageChange);
    };
  }, []);

  useEffect(() => {
    // If bed data is empty, open the bed management modal
    if (
      !searchParams.hideSetup &&
      !beds.isPlaceholderData &&
      beds.isSuccess &&
      !patientMonitors.isPlaceholderData &&
      patientMonitors.isSuccess &&
      (beds.data.length === 0 || !patientMonitors.data.some((monitor) => !!monitor.assignedBedId))
    ) {
      setBedManagementModal(true);
    }
  }, [
    beds.isPlaceholderData,
    beds.isSuccess,
    beds.data,
    patientMonitors.isSuccess,
    patientMonitors.isPlaceholderData,
    patientMonitors.data,
    searchParams.hideSetup,
  ]);

  useEffect(() => {
    if (!bedGroups.isPlaceholderData && bedGroups.isSuccess && !searchParams.hideSetup) {
      // If bedGroups data is empty, open the group management modal
      if (bedGroups.data.length === 0) setGroupManagementModal(true);
      else if (
        !activeGroup.current ||
        bedGroups.data.findIndex((group) => group.id === activeGroup.current) < 0
      ) {
        updateActiveGroup(bedGroups.data[0].id);
      }
    }
  }, [
    bedGroups.isPlaceholderData,
    bedGroups.isSuccess,
    bedGroups.data,
    updateActiveGroup,
    searchParams.hideSetup,
  ]);

  return (
    <PatientsData.Provider
      value={{
        getGroupById,
        getActiveGroup,
        selectedBed,
        updateActiveGroup,
        activeGroupId: activeGroup.current,
        loadingSelectedBed,
        updateSelectedBed,
        setBedManagementModal,
        bedManagementModalIsOpen,
        resetPatientsContext,
        bedsDisplayGroups,
        updateBedsOnDisplay,
        bedsDisplayGroupsKeepAlive,
        removeSelfFromBedsDisplayGroup,
        groupManagementModalIsOpen,
        setGroupManagementModal,
        monitorsFreshDataKeepAlive,
        resetMonitorsKeepAlive,
        updateKeepAlive,
      }}
    >
      {children}
    </PatientsData.Provider>
  );
};

export default PatientsContext;
