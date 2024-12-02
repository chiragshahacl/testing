import useAudioManager from '@/hooks/useAudioManager';
import { ALERT_PRIORITY, ALERT_TYPES, VITALS_ALERT_CODES } from '@/utils/metricCodes';

const TestComponent = () => {
  const {
    audioIsActive,
    audioAlarmSetting,
    autoPlayActivated,
    setAudioAlert,
    updateAudioSetting,
    activeAlertsExist,
    setActiveAlertsExist,
    setAutoPlayActivated,
    setTriggerStopAudio,
    currentAlertPriority,
    timerIsPaused,
  } = useAudioManager();

  const highPriority = [
    {
      type: ALERT_TYPES.VITALS,
      id: 'A-001',
      code: VITALS_ALERT_CODES.HR_HIGH_VISUAL.code,
      deviceCode: 'SP02',
      deviceId: '40000',
      priority: ALERT_PRIORITY.HIGH,
      acknowledged: false,
      timestamp: '2023-07-20T09:26:01.134',
    },
    {
      type: ALERT_TYPES.VITALS,
      id: 'A-002',
      code: VITALS_ALERT_CODES.RR_HIGH_VISUAL.code,
      deviceCode: 'SP02',
      deviceId: '40000',
      priority: ALERT_PRIORITY.MEDIUM,
      acknowledged: false,
      timestamp: '2023-07-20T09:26:07.934',
    },
    {
      type: ALERT_TYPES.VITALS,
      id: 'A-003',
      code: VITALS_ALERT_CODES.SPO2_HIGH_VISUAL.code,
      deviceCode: 'SP02',
      deviceId: '40000',
      priority: ALERT_PRIORITY.LOW,
      acknowledged: false,
      timestamp: '2023-07-20T09:26:07.934',
    },
  ];

  const medPriority = [
    {
      type: ALERT_TYPES.VITALS,
      id: 'A-002',
      code: VITALS_ALERT_CODES.RR_HIGH_VISUAL.code,
      deviceCode: 'SP02',
      deviceId: '40000',
      priority: ALERT_PRIORITY.MEDIUM,
      acknowledged: false,
      timestamp: '2023-07-20T09:26:07.934',
    },
    {
      type: ALERT_TYPES.VITALS,
      id: 'A-003',
      code: VITALS_ALERT_CODES.SPO2_HIGH_VISUAL.code,
      deviceCode: 'SP02',
      deviceId: '40000',
      priority: ALERT_PRIORITY.LOW,
      acknowledged: false,
      timestamp: '2023-07-20T09:26:07.934',
    },
  ];

  const lowPriority = [
    {
      type: ALERT_TYPES.VITALS,
      id: 'A-003',
      code: VITALS_ALERT_CODES.SPO2_HIGH_VISUAL.code,
      deviceCode: 'SP02',
      deviceId: '40000',
      priority: ALERT_PRIORITY.LOW,
      acknowledged: false,
      timestamp: '2023-07-20T09:26:07.934',
    },
  ];

  return (
    <>
      <p>activeAlertsExist: {`${activeAlertsExist}`}</p>
      <p>audioIsActive: {`${audioIsActive}`}</p>
      <p>audioAlarmSetting: {audioAlarmSetting}</p>
      <p>currentAlertPriority: {currentAlertPriority}</p>
      <p>timerIsPaused: {`${timerIsPaused}`}</p>
      <p>autoPlayActivated: {`${autoPlayActivated}`}</p>
      <button onClick={() => setAudioAlert(highPriority)}>setHighAudioAlert</button>
      <button onClick={() => setAudioAlert(medPriority)}>setMedAudioAlert</button>
      <button onClick={() => setAudioAlert(lowPriority)}>setLowAudioAlert</button>
      <button onClick={() => setActiveAlertsExist(true)}>setActiveAlertsExist</button>
      <button onClick={() => setAutoPlayActivated(true)}>setAutoPlayActivated</button>
      <button onClick={() => setTriggerStopAudio(true)}>setTriggerStopAudio</button>
      <button onClick={() => updateAudioSetting()}>updateAudioSetting</button>
    </>
  );
};

export default TestComponent;
