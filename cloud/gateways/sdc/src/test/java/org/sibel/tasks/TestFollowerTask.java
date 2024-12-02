package org.sibel.tasks;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

import com.google.common.util.concurrent.Futures;
import com.google.inject.Key;
import com.google.inject.name.Names;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.ExecutorService;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.sibel.BaseIntegrationTest;
import org.sibel.TestConstants;
import org.sibel.apis.DeviceApi;
import org.sibel.constants.*;
import org.sibel.exceptions.ApiRequestException;
import org.sibel.mdib.MdibAccessBuilder;
import org.sibel.mdib.MdibStateFactory;
import org.sibel.mdib.MdibUtils;
import org.sibel.models.DeviceDiscoveredBrokerMessage;
import org.sibel.models.NewVitalsRangesBrokerMessage;
import org.sibel.models.PatientSessionStartedBrokerMessage;
import org.sibel.models.api.ApiPatient;
import org.sibel.models.api.ApiPatientMonitorEncounter;
import org.sibel.models.payloads.AlertPayload;
import org.sibel.models.payloads.DeviceDiscoveredPayload;
import org.sibel.models.payloads.NewVitalsRangesPayload;
import org.sibel.models.payloads.PatientSessionStartedPayload;
import org.sibel.models.payloads.internal.*;
import org.somda.sdc.biceps.common.storage.PreprocessingException;
import org.somda.sdc.biceps.model.message.*;
import org.somda.sdc.biceps.model.participant.*;
import org.somda.sdc.biceps.provider.access.LocalMdibAccess;
import org.somda.sdc.dpws.client.Client;
import org.somda.sdc.dpws.model.ThisDeviceType;
import org.somda.sdc.dpws.service.HostingServiceProxy;
import org.somda.sdc.glue.consumer.PrerequisitesException;
import org.somda.sdc.glue.consumer.SdcRemoteDevicesConnector;
import org.somda.sdc.glue.consumer.sco.ScoTransaction;

public class TestFollowerTask extends BaseIntegrationTest {
    private static final String ANNE_CHEST_ID = "SEM-0001";
    private static final Instant METRIC_DETERMINATION_TIME = Instant.parse("2024-06-04T12:30:00Z");
    private static final Instant ALERT_DETERMINATION_TIME = Instant.parse("2024-06-04T12:00:00Z");
    private static final ApiPatient PLANNED_ENCOUNTER_PATIENT =
            new ApiPatient("internal_api_id", "P-002", "Anna", "Smith", "01-01-1980", FhirGenders.FEMALE, true);
    private static final PatientContextState PLANNED_ENCOUNTER_PATIENT_CONTEXT =
            MdibStateFactory.createPatientContextState(
                    PLANNED_ENCOUNTER_PATIENT.primaryIdentifier(),
                    PLANNED_ENCOUNTER_PATIENT.givenName(),
                    PLANNED_ENCOUNTER_PATIENT.familyName(),
                    PLANNED_ENCOUNTER_PATIENT.birthDate(),
                    MdibUtils.getSexFromFhirGender(PLANNED_ENCOUNTER_PATIENT.gender()),
                    ContextAssociation.ASSOC,
                    List.of(TestConstants.Settings.CENTRAL_HUB_VALIDATOR_ID));

    // Mocks
    private final ExecutorService executorMock;
    private final Client clientMock;
    private final SdcRemoteDevicesConnector sdcRemoteDevicesConnectorMock;

    // Task to test
    private FollowerTask followerTask;

    public TestFollowerTask() {
        super();

        executorMock = injector.getInstance(ExecutorService.class);
        clientMock = injector.getInstance(Key.get(Client.class, Names.named(DI.CLIENT)));
        sdcRemoteDevicesConnectorMock = injector.getInstance(SdcRemoteDevicesConnector.class);
    }

    @BeforeEach
    void setup() throws PreprocessingException, ApiRequestException {
        configureDefaultMocks();

        // Configure mocks
        configureSdcClientMock(TestConstants.CONNECTED_PM_ID);
        configureSetServiceAccessMock();
        configureDeviceApi(null);

        // Configure mdib
        var mdibAccess = createMdibAccess(TestConstants.CONNECTED_PATIENT, AlertActivation.ON);
        setConnectedPmMdibAccess(mdibAccess);

        // Reset mocks
        reset(executorMock);

        // Create task to test
        followerTask = injector.getInstance(FollowerTask.class);
    }

    public static Stream<Arguments> testDeviceDiscoveredWithValidPatient() {
        return Stream.of(
                // Test configuration payload, should send the correct value
                Arguments.of(AlertActivation.ON, false),
                Arguments.of(AlertActivation.PSD, false),
                Arguments.of(AlertActivation.OFF, false),

                // Test existing planned encounter, should send the same payload
                Arguments.of(AlertActivation.ON, true));
    }

    @ParameterizedTest
    @MethodSource
    void testDeviceDiscoveredWithValidPatient(AlertActivation alertActivation, boolean encounterPlanned)
            throws PreprocessingException, ApiRequestException {
        var mdibAccess = createMdibAccess(TestConstants.CONNECTED_PATIENT, alertActivation);
        setConnectedPmMdibAccess(mdibAccess);

        if (encounterPlanned) {
            configureDeviceApi(
                    new ApiPatientMonitorEncounter(EncounterStatus.PLANNED.getValue(), PLANNED_ENCOUNTER_PATIENT));
        }

        followerTask.handleDiscoveredDevice(TestConstants.CONNECTED_PM_DISCOVERED_DEVICE);

        verifyPmConnected();
        verifyDeviceDiscoveredNotificationSent(
                TestConstants.CONNECTED_PATIENT,
                alertActivation != AlertActivation.OFF,
                alertActivation == AlertActivation.PSD);
        verifyNewVitalRangesSent();
        verifySetPatientScoNotCalled();
        verifySessionStartedMessageSent();
    }

    @Test
    void testDeviceDiscoveredWithNoPatient() throws PreprocessingException {
        var mdibAccess = createMdibAccess(null, AlertActivation.ON);
        setConnectedPmMdibAccess(mdibAccess);

        followerTask.handleDiscoveredDevice(TestConstants.CONNECTED_PM_DISCOVERED_DEVICE);

        verifyPmConnected();
        verifyDeviceDiscoveredNotificationSent(null, true, false);
        verifyNewVitalRangesSent();
        verifySetPatientScoNotCalled();
    }

    public static Stream<Arguments> testDeviceDiscoveredWithPlannedEncounter() {
        return Stream.of(
                Arguments.of(null, true),
                Arguments.of(PatientPayload.createEmpty(ContextAssociation.NO), true),
                Arguments.of(
                        new PatientPayload(
                                "patient_search", null, null, null, (Sex) null, ContextAssociation.PRE, null),
                        true),
                Arguments.of(
                        new PatientPayload(
                                "patient_rejected", null, null, null, (Sex) null, ContextAssociation.NO, null),
                        true));
    }

    @ParameterizedTest
    @MethodSource
    void testDeviceDiscoveredWithPlannedEncounter(PatientPayload patient)
            throws PreprocessingException, ApiRequestException {
        var mdibAccess = createMdibAccess(patient, AlertActivation.ON);
        setConnectedPmMdibAccess(mdibAccess);

        configureDeviceApi(
                new ApiPatientMonitorEncounter(EncounterStatus.PLANNED.getValue(), PLANNED_ENCOUNTER_PATIENT));

        followerTask.handleDiscoveredDevice(TestConstants.CONNECTED_PM_DISCOVERED_DEVICE);

        verifyPmConnected();
        verifyDeviceDiscoveredNotificationSent(null, true, false);
        verifyNewVitalRangesSent();
        verifySetPatientScoCalled(List.of(PLANNED_ENCOUNTER_PATIENT_CONTEXT));
    }

    @Test
    void testDeviceDiscoveredWithPatientAlreadyInUse() throws PreprocessingException {
        var mdibAccess = createMdibAccess(TestConstants.CONNECTED_PATIENT, AlertActivation.ON);
        setConnectedPmMdibAccess(mdibAccess);

        configureRedisMock(true);

        followerTask.handleDiscoveredDevice(TestConstants.CONNECTED_PM_DISCOVERED_DEVICE);

        verifyPmConnected();
        verifyDeviceDiscoveredNotificationSent(null, true, false);
        verifyNewVitalRangesSent();
        verifySetPatientScoCalled(List.of(TestConstants.CONNECTED_PATIENT_CONTEXT_REJECTED));
    }

    @Test
    void testDeviceDiscoveredWithPlannedEncounterAndPatientAlreadyInUse()
            throws PreprocessingException, ApiRequestException {
        var mdibAccess = createMdibAccess(TestConstants.CONNECTED_PATIENT, AlertActivation.ON);
        setConnectedPmMdibAccess(mdibAccess);

        configureRedisMock(true);
        configureDeviceApi(
                new ApiPatientMonitorEncounter(EncounterStatus.PLANNED.getValue(), PLANNED_ENCOUNTER_PATIENT));

        followerTask.handleDiscoveredDevice(TestConstants.CONNECTED_PM_DISCOVERED_DEVICE);

        verifyPmConnected();
        verifyDeviceDiscoveredNotificationSent(null, true, false);
        verifyNewVitalRangesSent();

        // First reject the initial patient, then send the encounter
        verifySetPatientScoCalled(List.of(TestConstants.CONNECTED_PATIENT_CONTEXT_REJECTED));
        verifySetPatientScoCalled(List.of(PLANNED_ENCOUNTER_PATIENT_CONTEXT));
    }

    public static Stream<Arguments> testDeviceDiscoveredWithInvalidSerialNumber() {
        return Stream.of(
                Arguments.arguments(null, false),
                Arguments.arguments("", false),
                Arguments.arguments("-", false),
                Arguments.arguments(null, true),
                Arguments.arguments("", true),
                Arguments.arguments("-", true));
    }

    @ParameterizedTest
    @MethodSource
    void testDeviceDiscoveredWithInvalidSerialNumber(String serialNumber, boolean shouldFailToDisconnect) {
        configureSdcClientMock(serialNumber);

        if (shouldFailToDisconnect) {
            when(sdcRemoteDevicesConnectorMock.disconnect(anyString()))
                    .thenReturn(Futures.immediateFailedFuture(new RuntimeException("Failed to disconnect")));
        }

        followerTask.handleDiscoveredDevice(TestConstants.CONNECTED_PM_DISCOVERED_DEVICE);

        verifyPmClaimed();
        verifyPmAddedToRedisSet();
        verifyWatchdogObserverRegistered(true);
        verifyDeviceConnectionCheckTaskStarted(false);
        verifyConsumerReportProcessorRegistered(false);
        verifyPmReleased();
        verifyPmDisconnected();
    }

    @Test
    void testDeviceDiscoveredAlreadyClaimed() {
        // There is another consumer which handles the device
        when(redisMock.set(
                        eq(RedisKeys.getDeviceKey(TestConstants.CONNECTED_PM_EPR)),
                        eq(TestConstants.CONSUMER_ID),
                        any()))
                .thenReturn(null);

        followerTask.handleDiscoveredDevice(TestConstants.CONNECTED_PM_DISCOVERED_DEVICE);

        verifyPmClaimed();
        verifyWatchdogObserverRegistered(false);
        verifyDeviceConnectionCheckTaskStarted(false);
        verifyConsumerReportProcessorRegistered(false);
    }

    public static Stream<Arguments> testUnableToConnectToDevice() {
        return Stream.of(
                Arguments.arguments(true, false, false),
                Arguments.arguments(false, true, false),
                Arguments.arguments(false, false, true));
    }

    @ParameterizedTest
    @MethodSource
    void testUnableToConnectToDevice(
            boolean shouldClientConnectFutureFail,
            boolean shouldDeviceConnectThrowPrerequisiteException,
            boolean shouldDeviceConnectFutureFail) {
        // Configure possible exceptions when connecting to the device
        if (shouldClientConnectFutureFail) {
            when(clientMock.connect(TestConstants.CONNECTED_PM_DISCOVERED_DEVICE))
                    .thenReturn(Futures.immediateFailedFuture(new RuntimeException()));
        } else if (shouldDeviceConnectThrowPrerequisiteException) {
            try {
                when(sdcRemoteDevicesConnectorMock.connect(any(), any())).thenThrow(new PrerequisitesException());
            } catch (PrerequisitesException e) {
                fail("Error mocking SDC remove device connect");
            }
        } else if (shouldDeviceConnectFutureFail) {
            try {
                when(sdcRemoteDevicesConnectorMock.connect(any(), any()))
                        .thenReturn(Futures.immediateFailedFuture(new RuntimeException()));
            } catch (PrerequisitesException e) {
                fail("Error mocking SDC remove device connect");
            }
        }

        // Run the device discovery
        followerTask.handleDiscoveredDevice(TestConstants.CONNECTED_PM_DISCOVERED_DEVICE);

        verifyPmClaimed();
        verifyPmAddedToRedisSet();
        verifyWatchdogObserverRegistered(false);
        verifyDeviceConnectionCheckTaskStarted(false);
        verifyConsumerReportProcessorRegistered(false);
        verifyPmReleased();
    }

    private void verifyPmConnected() {
        verifyPmClaimed();
        verifyPmAddedToRedisSet();
        verifyWatchdogObserverRegistered(true);
        verifyDeviceConnectionCheckTaskStarted(true);
        verifyConsumerReportProcessorRegistered(true);
    }

    private void verifyPmClaimed() {
        verify(redisMock)
                .set(eq(RedisKeys.getDeviceKey(TestConstants.CONNECTED_PM_EPR)), eq(TestConstants.CONSUMER_ID), any());
    }

    private void verifyPmAddedToRedisSet() {
        verify(redisMock)
                .sadd(RedisKeys.getFollowerDevicesKey(TestConstants.CONSUMER_ID), TestConstants.CONNECTED_PM_EPR);
    }

    private void verifyPmReleased() {
        verify(redisMock).del(RedisKeys.getDeviceKey(TestConstants.CONNECTED_PM_EPR));
        verify(redisMock)
                .srem(RedisKeys.getFollowerDevicesKey(TestConstants.CONSUMER_ID), TestConstants.CONNECTED_PM_EPR);
    }

    private void verifyPmDisconnected() {
        verify(sdcRemoteDevicesConnectorMock).disconnect(TestConstants.CONNECTED_PM_EPR);
    }

    private void verifyWatchdogObserverRegistered(boolean wasRegistered) {
        verify(connectedSdcRemoteDeviceMock, wasRegistered ? times(1) : never()).registerWatchdogObserver(any());
    }

    private void verifyConsumerReportProcessorRegistered(boolean registered) {
        verify(mdibAccessObservableMock, registered ? times(1) : never())
                .registerObserver(any(ConsumerReportProcessor.class));
    }

    private void verifyDeviceConnectionCheckTaskStarted(boolean wasStarted) {
        verify(executorMock, wasStarted ? times(1) : never()).submit(any(DeviceConnectionCheckTask.class));
    }

    private void verifyDeviceDiscoveredNotificationSent(
            PatientPayload patientPayload, boolean audioEnabled, boolean audioPauseEnabled) {
        List<AlertPayload> technicalAlerts = List.of();
        if (patientPayload != null) {
            patientPayload.setAlerts(createPhysiologicalAlerts(patientPayload));
            technicalAlerts = createTechnicalAlerts(patientPayload);
        }

        var devicePayload = new DevicePayload(
                TestConstants.CONNECTED_PM_ID,
                SensorType.PM.code,
                null,
                SensorType.PM.code,
                List.of(new SensorPayload(ANNE_CHEST_ID, SensorType.ANNE_CHEST.code, SensorType.ANNE_CHEST.code)),
                technicalAlerts,
                new ConfigPayload(audioEnabled, audioPauseEnabled));
        var deviceDiscoveredMessage = new DeviceDiscoveredBrokerMessage(
                TestConstants.UUID_LIST.get(0),
                TestConstants.NOW,
                new DeviceDiscoveredPayload(devicePayload, patientPayload));
        kafkaProducerMock.verifyMessageSent(
                settings.KAFKA_TOPIC_DEVICE(), TestConstants.CONNECTED_PM_ID, deviceDiscoveredMessage, null);
    }

    private void verifyNewVitalRangesSent() {
        var rrAlertCondition = PhysiologicalAlert.RR_ME__VIS.condition;
        var leadOffAlertCondition = TechnicalAlert.LEAD_OFF.condition;
        var vitalRanges = List.of(
                new VitalsRangePayload(
                        leadOffAlertCondition.code,
                        leadOffAlertCondition.upperLimit,
                        leadOffAlertCondition.lowerLimit,
                        true),
                new VitalsRangePayload(
                        rrAlertCondition.code, rrAlertCondition.upperLimit, rrAlertCondition.lowerLimit, true));
        var newVitalsRangesMessage = new NewVitalsRangesBrokerMessage(
                TestConstants.UUID_LIST.get(1),
                TestConstants.NOW,
                new NewVitalsRangesPayload(TestConstants.CONNECTED_PM_ID, vitalRanges));
        kafkaProducerMock.verifyMessageSent(
                settings.KAFKA_TOPIC_DEVICE(), TestConstants.CONNECTED_PM_ID, newVitalsRangesMessage, null);
    }

    private void configureSetServiceAccessMock() {
        var invocationInfo = new InvocationInfo();
        invocationInfo.setInvocationState(InvocationState.FIN);
        var setContextStateResponse = new SetContextStateResponse();
        setContextStateResponse.setInvocationInfo(invocationInfo);
        var reportPart = new OperationInvokedReport.ReportPart();
        reportPart.setInvocationInfo(invocationInfo);

        ScoTransaction<SetContextStateResponse> setPatientContextResponse = mock();
        when(setPatientContextResponse.getResponse()).thenReturn(setContextStateResponse);
        when(setPatientContextResponse.waitForFinalReport(any())).thenReturn(List.of(reportPart));
    }

    private void verifySessionStartedMessageSent() {
        var message = new PatientSessionStartedBrokerMessage(
                TestConstants.UUID_LIST.get(2),
                TestConstants.NOW,
                new PatientSessionStartedPayload(TestConstants.CONNECTED_PM_ID, TestConstants.CONNECTED_PATIENT));
        kafkaProducerMock.verifyMessageSent(
                settings.KAFKA_TOPIC_DEVICE(), TestConstants.CONNECTED_PM_ID, message, null);
    }

    private void configureSdcClientMock(String pmId) {
        var hostingServiceProxyMock = createHostingServiceProxyMock(pmId);

        var clientMock = injector.getInstance(Key.get(Client.class, Names.named(DI.CLIENT)));
        reset(clientMock);
        when(clientMock.connect(TestConstants.CONNECTED_PM_DISCOVERED_DEVICE))
                .thenReturn(Futures.immediateFuture(hostingServiceProxyMock));
    }

    private void configureDeviceApi(ApiPatientMonitorEncounter encounter) throws ApiRequestException {
        var deviceApi = injector.getInstance(DeviceApi.class);
        reset(deviceApi);
        when(deviceApi.getDeviceEncounter(any())).thenReturn(encounter);
    }

    private LocalMdibAccess createMdibAccess(PatientPayload patient, AlertActivation audioActivation)
            throws PreprocessingException {
        var builder = new MdibAccessBuilder()
                .addDevice(SensorType.ANNE_CHEST, ANNE_CHEST_ID)
                .addMetricChannel(SensorType.ANNE_CHEST, MetricChannel.DEVICE)
                .addMetricChannel(SensorType.ANNE_CHEST, MetricChannel.VITALS)
                .addMetric(SensorType.ANNE_CHEST, Metric.DEVICE_LEAD, "true", METRIC_DETERMINATION_TIME)
                .addMetric(SensorType.ANNE_CHEST, Metric.RR_METRIC, BigDecimal.ONE, METRIC_DETERMINATION_TIME)
                .addAlertSystem(SensorType.PM, audioActivation)
                .addAlertSystem(SensorType.ANNE_CHEST)
                .addAlert(SensorType.ANNE_CHEST, TechnicalAlert.LEAD_OFF, true, ALERT_DETERMINATION_TIME)
                .addAlert(PhysiologicalAlert.RR_ME__VIS, false, ALERT_DETERMINATION_TIME, false)
                .addSco(SensorType.PM)
                .addScoOperation(SensorType.PM, ScoOperationType.SET_CONTEXT_STATE);
        if (patient != null) {
            builder.addPatient(
                    patient.getPrimaryIdentifier(),
                    patient.getGivenName(),
                    patient.getFamilyName(),
                    patient.getBirthDate(),
                    patient.getGender(),
                    patient.getAssociation(),
                    patient.getValidators());
        }
        return builder.build();
    }

    private static List<AlertPayload> createTechnicalAlerts(PatientPayload patientPayload) {
        var leadOffAlertPayload = new AlertPayload(
                patientPayload.getPrimaryIdentifier(),
                true,
                false,
                TechnicalAlert.LEAD_OFF.code,
                SensorType.ANNE_CHEST.code,
                TechnicalAlert.LEAD_OFF.priority.toString(),
                ALERT_DETERMINATION_TIME,
                ANNE_CHEST_ID,
                new VitalsRangePayload(
                        TechnicalAlert.LEAD_OFF.condition.code,
                        TechnicalAlert.LEAD_OFF.condition.upperLimit,
                        TechnicalAlert.LEAD_OFF.condition.lowerLimit,
                        true));
        return List.of(leadOffAlertPayload);
    }

    private static List<AlertPayload> createPhysiologicalAlerts(PatientPayload patientPayload) {
        var rrHiAlertPayload = new AlertPayload(
                patientPayload.getPrimaryIdentifier(),
                false,
                false,
                PhysiologicalAlert.RR_ME__VIS.code,
                SensorType.ANNE_CHEST.code,
                PhysiologicalAlert.RR_ME__VIS.priority.toString(),
                ALERT_DETERMINATION_TIME,
                ANNE_CHEST_ID,
                null);
        return List.of(rrHiAlertPayload);
    }

    private static HostingServiceProxy createHostingServiceProxyMock(String pmId) {
        var thisDeviceTypeMock = createThisDeviceTypeMock(pmId);

        HostingServiceProxy hostingServiceProxyMock = mock();
        when(hostingServiceProxyMock.getThisDevice()).thenReturn(Optional.of(thisDeviceTypeMock));
        return hostingServiceProxyMock;
    }

    private static ThisDeviceType createThisDeviceTypeMock(String pmId) {
        ThisDeviceType thisDeviceTypeMock = mock();
        when(thisDeviceTypeMock.getSerialNumber()).thenReturn(pmId);
        return thisDeviceTypeMock;
    }
}
