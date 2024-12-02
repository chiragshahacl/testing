package org.sibel.tasks;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;
import static org.sibel.mdib.MdibStateFactory.*;

import java.math.BigDecimal;
import java.time.*;
import java.util.*;
import java.util.stream.Stream;
import org.apache.kafka.common.header.internals.RecordHeader;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.sibel.BaseIntegrationTest;
import org.sibel.TestConstants;
import org.sibel.apis.EhrApi;
import org.sibel.constants.*;
import org.sibel.exceptions.ActionOnDisconnectedPatientMonitor;
import org.sibel.exceptions.ApiRequestException;
import org.sibel.factories.ConsumerReportProcessorFactory;
import org.sibel.mdib.MdibAccessBuilder;
import org.sibel.mdib.MdibStateFactory;
import org.sibel.models.*;
import org.sibel.models.api.EhrPatient;
import org.sibel.models.payloads.*;
import org.sibel.models.payloads.internal.ConfigPayload;
import org.sibel.models.payloads.internal.DevicePayload;
import org.sibel.models.payloads.internal.PatientPayload;
import org.sibel.models.payloads.internal.VitalsRangePayload;
import org.somda.sdc.biceps.common.MdibEntity;
import org.somda.sdc.biceps.common.access.MdibAccess;
import org.somda.sdc.biceps.common.event.*;
import org.somda.sdc.biceps.common.storage.PreprocessingException;
import org.somda.sdc.biceps.model.participant.*;
import org.somda.sdc.biceps.provider.access.LocalMdibAccess;

class TestConsumerReportProcessor extends BaseIntegrationTest {
    private enum DescriptionModificationMessageType {
        CREATE,
        UPDATE,
        DELETE
    }

    public static final String ANNE_CHEST_ID = "SEM-001";
    private static final Instant METRIC_DETERMINATION_TIME = Instant.parse("2023-10-31T08:30:00Z");
    private static final Instant ALERT_DETERMINATION_TIME = Instant.parse("2023-10-31T08:00:03Z");
    private static final List<BigDecimal> WAVEFORM_SAMPLE = List.of(
            BigDecimal.valueOf(0.09),
            BigDecimal.valueOf(0.08),
            BigDecimal.valueOf(0.07),
            BigDecimal.valueOf(0.06),
            BigDecimal.valueOf(0.05),
            BigDecimal.valueOf(0.06),
            BigDecimal.valueOf(0.07),
            BigDecimal.valueOf(0.08),
            BigDecimal.valueOf(0.09));
    private static final EhrPatient EHR_PATIENT_1 =
            new EhrPatient(List.of("EHR-001", "ehr001"), "John", "Doe", "19900101", Hl7Genders.MALE);
    private static final EhrPatient EHR_PATIENT_2 =
            new EhrPatient(List.of("EHR-002", "ehr002"), "John", "Doe", "19800101", Hl7Genders.MALE);
    private static final PatientContextState EHR_PATIENT_CONTEXT_1 = createPatientContextState(
            EHR_PATIENT_1.patientIdentifiers().stream().findFirst().orElseThrow(),
            EHR_PATIENT_1.givenName(),
            EHR_PATIENT_1.familyName(),
            "1990-01-01",
            Sex.M,
            ContextAssociation.PRE,
            List.of(TestConstants.Settings.CENTRAL_HUB_VALIDATOR_ID));
    private static final PatientContextState EHR_PATIENT_CONTEXT_2 = createPatientContextState(
            EHR_PATIENT_2.patientIdentifiers().stream().findFirst().orElseThrow(),
            EHR_PATIENT_2.givenName(),
            EHR_PATIENT_2.familyName(),
            "1980-01-01",
            Sex.M,
            ContextAssociation.PRE,
            List.of(TestConstants.Settings.CENTRAL_HUB_VALIDATOR_ID));
    private static final PatientContextState EMPTY_EHR_CONTEXT_RESULT = createPatientContextState(
            "Unknown",
            null,
            null,
            null,
            null,
            ContextAssociation.NO,
            List.of(TestConstants.Settings.CENTRAL_HUB_VALIDATOR_ID));

    private ConsumerReportProcessor processor;

    @BeforeEach
    void setUp() {
        configureDefaultMocks();

        // Configure the processor
        var processorFactory = injector.getInstance(ConsumerReportProcessorFactory.class);
        processor = processorFactory.create(TestConstants.CONNECTED_PM_ID);
    }

    public static Stream<Arguments> testDeviceBatteryChangeReceived() {
        return Stream.of(
                Arguments.arguments(
                        ANNE_CHEST_ID, SensorType.ANNE_CHEST, BigDecimal.valueOf(75), BatteryState.ChargeStatus.CH_B),
                Arguments.arguments(
                        TestConstants.CONNECTED_PM_ID,
                        SensorType.PM,
                        BigDecimal.valueOf(66),
                        BatteryState.ChargeStatus.DIS_CH_B));
    }

    @ParameterizedTest
    @MethodSource
    void testDeviceBatteryChangeReceived(
            String devicePrimaryIdentifier,
            SensorType sensorType,
            BigDecimal remainingBattery,
            BatteryState.ChargeStatus chargeStatus)
            throws PreprocessingException {
        var modificationMessage = createComponentStateModificationMessage(
                sensorType, devicePrimaryIdentifier, remainingBattery, chargeStatus);
        processor.onComponentChange(modificationMessage);

        var expectedMessage = new MetricBrokerMessage<>(
                TestConstants.UUID_LIST.get(0),
                TestConstants.NOW,
                new MetricPayload<>(
                        TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                        List.of(remainingBattery),
                        TestConstants.NOW, // Battery has no determination time, so it uses now
                        Metric.BATTERY.code,
                        Metric.BATTERY.unitCode,
                        sensorType.code,
                        devicePrimaryIdentifier));
        var expectedMessageHeaders = List.of(
                new RecordHeader(KafkaHeaders.CODE, Metric.BATTERY.code.getBytes()),
                new RecordHeader(KafkaHeaders.DEVICE_PRIMARY_IDENTIFIER, devicePrimaryIdentifier.getBytes()));
        kafkaProducerMock.verifyMessageSent(
                settings.KAFKA_TOPIC_VITALS(),
                TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                expectedMessage,
                expectedMessageHeaders);

        var chargeStatusCode = "%s-S".formatted(Metric.BATTERY.code);
        var expectedChargeStatusMessage = new MetricBrokerMessage<>(
                TestConstants.UUID_LIST.get(1),
                TestConstants.NOW,
                new MetricPayload<>(
                        TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                        List.of(chargeStatus.value()),
                        TestConstants.NOW, // Battery has no determination time, so it uses now
                        chargeStatusCode,
                        UnitCodes.NO_UNIT,
                        sensorType.code,
                        devicePrimaryIdentifier));
        var expectedChargeStatusMessageHeaders = List.of(
                new RecordHeader(KafkaHeaders.CODE, chargeStatusCode.getBytes()),
                new RecordHeader(KafkaHeaders.DEVICE_PRIMARY_IDENTIFIER, devicePrimaryIdentifier.getBytes()));
        kafkaProducerMock.verifyMessageSent(
                settings.KAFKA_TOPIC_VITALS(),
                TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                expectedChargeStatusMessage,
                expectedChargeStatusMessageHeaders);
    }

    @Test
    void testDeviceBatteryChangeReceivedWithoutPatientData() throws PreprocessingException {
        connectDefaultPatientMonitor(null); // No patient
        var modificationMessage = createComponentStateModificationMessage(
                SensorType.ANNE_CHEST, ANNE_CHEST_ID, BigDecimal.valueOf(75), BatteryState.ChargeStatus.DIS_CH_B);
        processor.onComponentChange(modificationMessage);
        kafkaProducerMock.verifyNoMessagesSent();
    }

    public static Stream<Arguments> testMetricChangeReceived() {
        return Stream.of(
                Arguments.arguments(Metric.HR, BigDecimal.valueOf(101)),
                Arguments.arguments(Metric.BODY_POSITION, "SUPINE"));
    }

    @ParameterizedTest
    @MethodSource
    void testMetricChangeReceived(Metric metric, Object metricValue) throws PreprocessingException {
        var devicePrimaryIdentifier = ANNE_CHEST_ID;

        var modificationMessage = createMetricChangeModificationMessage(
                devicePrimaryIdentifier, metric, metricValue, MeasurementValidity.VLD);
        processor.onMetricChange(modificationMessage);

        var unitCode = metricValue instanceof BigDecimal ? metric.unitCode : null; // String values have no unit
        var expectedMessage = new MetricBrokerMessage<>(
                TestConstants.UUID_LIST.get(0),
                TestConstants.NOW,
                new MetricPayload<>(
                        TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                        List.of(metricValue),
                        METRIC_DETERMINATION_TIME,
                        metric.code,
                        unitCode,
                        SensorType.ANNE_CHEST.code,
                        devicePrimaryIdentifier));
        var expectedMessageHeaders = List.of(
                new RecordHeader(KafkaHeaders.CODE, metric.code.getBytes()),
                new RecordHeader(KafkaHeaders.DEVICE_PRIMARY_IDENTIFIER, devicePrimaryIdentifier.getBytes()));
        kafkaProducerMock.verifyMessageSent(
                settings.KAFKA_TOPIC_VITALS(),
                TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                expectedMessage,
                expectedMessageHeaders);
    }

    /* This tests the IEEE 11073-20701 requirement R0048:
    An SDC SERVICE CONSUMER SHALL utilize only METRICs where pm:MetricQuality/@Validity
    is either valid or validated if erroneous information results in an unacceptable RISK.
    */
    public static Stream<Arguments> testInvalidMetricChangeReceived() {
        return Stream.of(
                Arguments.arguments(Metric.HR, BigDecimal.valueOf(101)),
                Arguments.arguments(Metric.BODY_POSITION, "SUPINE"));
    }

    @ParameterizedTest
    @MethodSource
    void testInvalidMetricChangeReceived(Metric metric, Object metricValue) throws PreprocessingException {

        var modificationMessage =
                createMetricChangeModificationMessage(ANNE_CHEST_ID, metric, metricValue, MeasurementValidity.INV);

        processor.onMetricChange(modificationMessage);

        kafkaProducerMock.verifyNoMessagesSent();
    }

    @Test
    void testMetricChangeReceivedWithoutPatientData() throws PreprocessingException {
        connectDefaultPatientMonitor(null); // No patient
        var modificationMessage = createMetricChangeModificationMessage(
                ANNE_CHEST_ID, Metric.HR, BigDecimal.valueOf(50), MeasurementValidity.VLD);
        processor.onMetricChange(modificationMessage);
        kafkaProducerMock.verifyNoMessagesSent();
    }

    @Test
    void testWaveformChangeReceived() throws PreprocessingException {
        var devicePrimaryIdentifier = ANNE_CHEST_ID;
        var metric = Metric.ECG_WAVEFORM;
        var samplePeriod = Duration.ofMillis(100);
        var determinationPeriod = Duration.ofMillis(200);

        var modificationMessage = createWaveformChangeModificationMessage(
                devicePrimaryIdentifier, metric, samplePeriod, determinationPeriod, METRIC_DETERMINATION_TIME);
        processor.onWaveformChange(modificationMessage);

        var expectedMessage = new WaveformBrokerMessage(
                TestConstants.UUID_LIST.get(0),
                TestConstants.NOW,
                new WaveformPayload(
                        TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                        WAVEFORM_SAMPLE,
                        METRIC_DETERMINATION_TIME,
                        samplePeriod,
                        determinationPeriod,
                        metric.code,
                        SensorType.ANNE_CHEST.code,
                        devicePrimaryIdentifier));
        var expectedMessageHeaders = List.of(
                new RecordHeader("code", metric.code.getBytes()),
                new RecordHeader("device_primary_identifier", devicePrimaryIdentifier.getBytes()));
        kafkaProducerMock.verifyMessageSent(
                settings.KAFKA_TOPIC_VITALS(),
                TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                expectedMessage,
                expectedMessageHeaders);
    }

    @Test
    void testWaveformChangeReceivedWithoutPatientData() throws PreprocessingException {
        connectDefaultPatientMonitor(null); // No patient
        var modificationMessage = createWaveformChangeModificationMessage(
                ANNE_CHEST_ID,
                Metric.ECG_WAVEFORM,
                Duration.ofMillis(100),
                Duration.ofMillis(100),
                LocalDate.parse("2023-10-31").atStartOfDay().toInstant(ZoneOffset.UTC));
        processor.onWaveformChange(modificationMessage);
        kafkaProducerMock.verifyNoMessagesSent();
    }

    public static Stream<Arguments> testTechnicalAlertChangeReceived() {
        return Stream.of(
                Arguments.arguments(true, true),
                Arguments.arguments(true, false),
                Arguments.arguments(false, true),
                Arguments.arguments(false, false));
    }

    @ParameterizedTest
    @MethodSource
    void testTechnicalAlertChangeReceived(boolean withSources, boolean withDeterminationTime)
            throws PreprocessingException {
        var deviceType = SensorType.ANNE_CHEST;
        var devicePrimaryIdentifier = ANNE_CHEST_ID;
        var alert = TechnicalAlert.LEAD_OFF;
        var alertEnabled = true;

        var modificationMessage = createAlertChangeModificationMessage(
                deviceType, devicePrimaryIdentifier, alert, alertEnabled, withSources, withDeterminationTime);
        processor.onAlertChange(modificationMessage);

        var expectedDeterminationTime = withDeterminationTime
                ? ALERT_DETERMINATION_TIME
                : withSources ? METRIC_DETERMINATION_TIME : TestConstants.NOW;
        var expectedMessage = new AlertBrokerMessage(
                TestConstants.UUID_LIST.get(0),
                TestConstants.NOW,
                new AlertPayload(
                        TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                        alertEnabled,
                        false,
                        alert.code,
                        deviceType.code,
                        alert.priority.toString(),
                        expectedDeterminationTime,
                        devicePrimaryIdentifier,
                        new VitalsRangePayload(
                                alert.condition.code, alert.condition.upperLimit, alert.condition.lowerLimit, true)));
        var expectedMessageHeaders = List.of(new RecordHeader(
                KafkaHeaders.PATIENT_PRIMARY_IDENTIFIER,
                TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier().getBytes()));
        kafkaProducerMock.verifyMessageSent(
                settings.KAFKA_TOPIC_DEVICE(), TestConstants.CONNECTED_PM_ID, expectedMessage, expectedMessageHeaders);
    }

    @Test
    void testTechnicalAlertChangeReceivedWithoutPatientData() throws PreprocessingException {
        connectDefaultPatientMonitor(null); // No patient
        var modificationMessage = createAlertChangeModificationMessage(
                SensorType.ANNE_CHEST, ANNE_CHEST_ID, TechnicalAlert.LEAD_OFF, true, true, true);
        processor.onAlertChange(modificationMessage);
        kafkaProducerMock.verifyNoMessagesSent();
    }

    @Test
    void testPhysiologicalAlertChangeReceived() throws PreprocessingException {
        var modificationMessage = createAlertChangeModificationMessage(
                SensorType.ANNE_CHEST, ANNE_CHEST_ID, PhysiologicalAlert.RR_ME__VIS, true);
        processor.onAlertChange(modificationMessage);

        var expectedMessage = new AlertBrokerMessage(
                TestConstants.UUID_LIST.get(0),
                TestConstants.NOW,
                new AlertPayload(
                        TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                        true,
                        false,
                        PhysiologicalAlert.RR_ME__VIS.code,
                        SensorType.ANNE_CHEST.code,
                        PhysiologicalAlert.RR_ME__VIS.priority.toString(),
                        ALERT_DETERMINATION_TIME,
                        ANNE_CHEST_ID,
                        new VitalsRangePayload(
                                PhysiologicalAlert.RR_ME__VIS.condition.code,
                                PhysiologicalAlert.RR_ME__VIS.condition.upperLimit,
                                PhysiologicalAlert.RR_ME__VIS.condition.lowerLimit,
                                true)));
        kafkaProducerMock.verifyMessageSent(
                settings.KAFKA_TOPIC_ALERT(),
                TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                expectedMessage,
                null);
    }

    @Test
    void testPhysiologicalAlertWithLatchingReceivedWhereConditionIsTrue() throws PreprocessingException {
        var modificationMessage = createAlertChangeModificationMessage(
                SensorType.ANNE_CHEST, ANNE_CHEST_ID, PhysiologicalAlert.RR_ME__VIS, true, true);
        processor.onAlertChange(modificationMessage);

        var expectedMessage = new AlertBrokerMessage(
                TestConstants.UUID_LIST.get(0),
                TestConstants.NOW,
                new AlertPayload(
                        TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                        true,
                        false,
                        PhysiologicalAlert.RR_ME__VIS.code,
                        SensorType.ANNE_CHEST.code,
                        PhysiologicalAlert.RR_ME__VIS.priority.toString(),
                        ALERT_DETERMINATION_TIME,
                        ANNE_CHEST_ID,
                        new VitalsRangePayload(
                                PhysiologicalAlert.RR_ME__VIS.condition.code,
                                PhysiologicalAlert.RR_ME__VIS.condition.upperLimit,
                                PhysiologicalAlert.RR_ME__VIS.condition.lowerLimit,
                                true)));
        kafkaProducerMock.verifyMessageSent(
                settings.KAFKA_TOPIC_ALERT(),
                TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                expectedMessage,
                null);
    }

    @Test
    void testPhysiologicalAlertWithLatchingReceivedWhereConditionIsFalse() throws PreprocessingException {
        var modificationMessage = createAlertChangeModificationMessage(
                SensorType.ANNE_CHEST, ANNE_CHEST_ID, PhysiologicalAlert.RR_ME__VIS, false, true);
        processor.onAlertChange(modificationMessage);

        var expectedMessage = new AlertBrokerMessage(
                TestConstants.UUID_LIST.get(0),
                TestConstants.NOW,
                new AlertPayload(
                        TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                        true,
                        true,
                        PhysiologicalAlert.RR_ME__VIS.code,
                        SensorType.ANNE_CHEST.code,
                        PhysiologicalAlert.RR_ME__VIS.priority.toString(),
                        ALERT_DETERMINATION_TIME,
                        ANNE_CHEST_ID,
                        new VitalsRangePayload(
                                PhysiologicalAlert.RR_ME__VIS.condition.code,
                                PhysiologicalAlert.RR_ME__VIS.condition.upperLimit,
                                PhysiologicalAlert.RR_ME__VIS.condition.lowerLimit,
                                true)));
        kafkaProducerMock.verifyMessageSent(
                settings.KAFKA_TOPIC_ALERT(),
                TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                expectedMessage,
                null);
    }

    @Test
    void testPhysiologicalAlertChangeReceivedWithoutPatientData()
            throws PreprocessingException, ActionOnDisconnectedPatientMonitor {
        connectDefaultPatientMonitor(null); // No patient
        var modificationMessage = createAlertChangeModificationMessage(
                SensorType.ANNE_CHEST, ANNE_CHEST_ID, PhysiologicalAlert.RR_ME__VIS, true);
        processor.onAlertChange(modificationMessage);
        kafkaProducerMock.verifyNoMessagesSent();
    }

    @Test
    void testLimitAlertChangeReceived() throws PreprocessingException {
        var alerts = List.of(PhysiologicalAlert.RR_ME__VIS, PhysiologicalAlert.HR_ME__VIS);

        var modificationMessage =
                createLimitAlertChangeModificationMessage(SensorType.ANNE_CHEST, ANNE_CHEST_ID, alerts);
        processor.onAlertChange(modificationMessage);

        var vitalsRangePayloads = alerts.stream()
                .map(alert -> new VitalsRangePayload(
                        alert.condition.code, alert.condition.upperLimit, alert.condition.lowerLimit, true))
                .toList();
        var message = new NewVitalsRangesBrokerMessage(
                TestConstants.UUID_LIST.get(0),
                TestConstants.NOW,
                new NewVitalsRangesPayload(TestConstants.CONNECTED_PM_ID, vitalsRangePayloads));
        kafkaProducerMock.verifyMessageSent(
                settings.KAFKA_TOPIC_DEVICE(), TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(), message, null);
    }

    @Test
    void testLimitAlertChangeReceivedWithoutPatientData() throws PreprocessingException {
        connectDefaultPatientMonitor(null); // No patient

        var alerts = List.of(PhysiologicalAlert.RR_ME__VIS, PhysiologicalAlert.HR_ME__VIS);

        var modificationMessage =
                createLimitAlertChangeModificationMessage(SensorType.ANNE_CHEST, ANNE_CHEST_ID, alerts);
        processor.onAlertChange(modificationMessage);

        kafkaProducerMock.verifyNoMessagesSent();
    }

    @Test
    void testDeletedPatientContextChangeReceived() throws PreprocessingException {
        var modificationMessage = createPatientModificationMessage(
                TestConstants.CONNECTED_PATIENT, DescriptionModificationMessageType.DELETE);
        processor.onContextChange(modificationMessage);

        var expectedMessage = new PatientSessionClosedBrokerMessage(
                TestConstants.UUID_LIST.get(0),
                TestConstants.NOW,
                new PatientSessionClosedPayload(
                        TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(), TestConstants.CONNECTED_PM_ID));
        kafkaProducerMock.verifyMessageSent(
                settings.KAFKA_TOPIC_DEVICE(), TestConstants.CONNECTED_PM_ID, expectedMessage, null);
    }

    public static Stream<Arguments> testEmptyPatientContextReceived() {
        return Stream.of(
                Arguments.of(DescriptionModificationMessageType.CREATE),
                Arguments.of(DescriptionModificationMessageType.UPDATE));
    }

    @ParameterizedTest
    @MethodSource
    void testEmptyPatientContextReceived(DescriptionModificationMessageType messageType) throws PreprocessingException {
        var modificationMessage =
                createPatientModificationMessage(PatientPayload.createEmpty(ContextAssociation.ASSOC), messageType);
        processor.onContextChange(modificationMessage);

        var expectedMessage = new PatientSessionClosedBrokerMessage(
                TestConstants.UUID_LIST.get(0),
                TestConstants.NOW,
                new PatientSessionClosedPayload(null, TestConstants.CONNECTED_PM_ID));
        kafkaProducerMock.verifyMessageSent(
                settings.KAFKA_TOPIC_DEVICE(), TestConstants.CONNECTED_PM_ID, expectedMessage, null);
    }

    @Test
    void testValidatedPatientContextReceived() throws PreprocessingException {
        var modificationMessage = createPatientModificationMessage(
                TestConstants.CONNECTED_PATIENT, DescriptionModificationMessageType.UPDATE);
        processor.onContextChange(modificationMessage);

        var expectedMessage = new PatientSessionStartedBrokerMessage(
                TestConstants.UUID_LIST.get(0),
                TestConstants.NOW,
                new PatientSessionStartedPayload(TestConstants.CONNECTED_PM_ID, TestConstants.CONNECTED_PATIENT));
        kafkaProducerMock.verifyMessageSent(
                settings.KAFKA_TOPIC_DEVICE(), TestConstants.CONNECTED_PM_ID, expectedMessage, null);
    }

    public static Stream<Arguments> testEhrSearchReceived() {
        return Stream.of(
                Arguments.of(List.of(), List.of(EMPTY_EHR_CONTEXT_RESULT)),
                Arguments.of(
                        List.of(EHR_PATIENT_1, EHR_PATIENT_2), List.of(EHR_PATIENT_CONTEXT_1, EHR_PATIENT_CONTEXT_2)));
    }

    @ParameterizedTest
    @MethodSource
    void testEhrSearchReceived(List<EhrPatient> ehrPatients, List<PatientContextState> contextStatesSentToPm)
            throws PreprocessingException, ApiRequestException {
        var modificationMessage = createPatientModificationMessage(
                new PatientPayload("search_criteria", null, null, null, Sex.UNKN, ContextAssociation.PRE, null),
                DescriptionModificationMessageType.UPDATE);
        configureEhrApi(ehrPatients);
        processor.onContextChange(modificationMessage);

        verifySetPatientScoCalled(contextStatesSentToPm);
        kafkaProducerMock.verifyNoMessagesSent();
    }

    @Test
    void testPatientAlreadyInUseReceived() throws PreprocessingException {
        var modificationMessage = createPatientModificationMessage(
                TestConstants.CONNECTED_PATIENT, DescriptionModificationMessageType.UPDATE);
        configureRedisMock(true);
        processor.onContextChange(modificationMessage);

        verifySetPatientScoCalled(List.of(TestConstants.CONNECTED_PATIENT_CONTEXT_REJECTED));
        kafkaProducerMock.verifyNoMessagesSent();
    }

    @Test
    void testPatientRejectedReceived() throws PreprocessingException {
        var modificationMessage = createPatientModificationMessage(
                TestConstants.CONNECTED_PATIENT_REJECTED, DescriptionModificationMessageType.UPDATE);
        processor.onContextChange(modificationMessage);

        var payload = new PatientAdmissionRejectedPayload(
                TestConstants.CONNECTED_PM_ID, TestConstants.CONNECTED_PATIENT_REJECTED.getPrimaryIdentifier());
        var message =
                new PatientAdmissionRejectedBrokerMessage(TestConstants.UUID_LIST.get(0), TestConstants.NOW, payload);
        kafkaProducerMock.verifyMessageSent(
                settings.KAFKA_TOPIC_DEVICE(), TestConstants.CONNECTED_PM_ID, message, null);
    }

    @Test
    void testUnknownPatientContextReceived() throws PreprocessingException {
        var modificationMessage = createPatientModificationMessage(
                new PatientPayload("some_id", null, null, null, Sex.M, ContextAssociation.DIS, null),
                DescriptionModificationMessageType.UPDATE);
        processor.onContextChange(modificationMessage);

        kafkaProducerMock.verifyNoMessagesSent();
    }

    @Test
    void testDeletedSensorChangeReceived() throws PreprocessingException {
        var devicePrimaryIdentifier = ANNE_CHEST_ID;

        var modificationMessage = createDeletedSensorModificationMessage(devicePrimaryIdentifier);
        processor.onContextChange(modificationMessage);

        var expectedMessage = new SensorRemovedBrokerMessage(
                TestConstants.UUID_LIST.get(0),
                TestConstants.NOW,
                new SensorRemovedPayload(
                        devicePrimaryIdentifier,
                        TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                        TestConstants.NOW));
        kafkaProducerMock.verifyMessageSent(
                settings.KAFKA_TOPIC_DEVICE(), TestConstants.CONNECTED_PM_ID, expectedMessage, null);
    }

    @Test
    void testSensorChangeReceived() throws PreprocessingException {
        var modificationMessage = createUpdatedSensorModificationMessage();
        processor.onContextChange(modificationMessage);

        var devicePayload = new DevicePayload(
                ANNE_CHEST_ID,
                SensorType.ANNE_CHEST.code,
                TestConstants.CONNECTED_PM_ID,
                SensorType.ANNE_CHEST.code,
                null,
                List.of(),
                new ConfigPayload(true, false));
        var expectedMessage = new DeviceDiscoveredBrokerMessage(
                TestConstants.UUID_LIST.get(0),
                TestConstants.NOW,
                new DeviceDiscoveredPayload(devicePayload, TestConstants.CONNECTED_PATIENT));
        kafkaProducerMock.verifyMessageSent(
                settings.KAFKA_TOPIC_DEVICE(), TestConstants.CONNECTED_PM_ID, expectedMessage, null);
    }

    @Test
    void testSensorChangeReceivedWithoutPatient() throws PreprocessingException {
        connectDefaultPatientMonitor(null); // No patient
        var modificationMessage = createUpdatedSensorModificationMessage();
        processor.onContextChange(modificationMessage);
        kafkaProducerMock.verifyNoMessagesSent();
    }

    // TODO: WHY THIS EVENT IS TRIGGERED BY 2 DIFFERENT METHODS (testLimitAlertChangeReceived)?
    @Test
    void testLimitDescriptionChangeReceived() throws PreprocessingException {
        var alerts = List.of(PhysiologicalAlert.RR_ME__VIS, PhysiologicalAlert.HR_ME__VIS);
        var modificationMessage = createLimitDescriptionModificationMessage(alerts);
        processor.onContextChange(modificationMessage);

        var vitalsRangePayloads = alerts.stream()
                .map(alert -> new VitalsRangePayload(
                        alert.condition.code, alert.condition.upperLimit, alert.condition.lowerLimit, true))
                .toList();
        var expectedMessage = new NewVitalsRangesBrokerMessage(
                TestConstants.UUID_LIST.get(0),
                TestConstants.NOW,
                new NewVitalsRangesPayload(TestConstants.CONNECTED_PM_ID, vitalsRangePayloads));
        kafkaProducerMock.verifyMessageSent(
                settings.KAFKA_TOPIC_DEVICE(),
                TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                expectedMessage,
                null);
    }

    @Test
    void testLimitDescriptionChangeReceivedWithoutPatient() throws PreprocessingException {
        connectDefaultPatientMonitor(null); // No patient
        var alerts = List.of(PhysiologicalAlert.RR_ME__VIS, PhysiologicalAlert.HR_ME__VIS);

        var modificationMessage = createLimitDescriptionModificationMessage(alerts);
        processor.onContextChange(modificationMessage);

        kafkaProducerMock.verifyNoMessagesSent();
    }

    public static Stream<Arguments> testPmConfigurationUpdated() {
        return Stream.of(
                Arguments.of(AlertActivation.ON), Arguments.of(AlertActivation.PSD), Arguments.of(AlertActivation.OFF));
    }

    @ParameterizedTest
    @MethodSource
    void testPmConfigurationUpdated(AlertActivation audioActivation) throws PreprocessingException {
        var modificationMessage = createAlertSystemModificationMessage(audioActivation);
        processor.onAlertChange(modificationMessage);

        var expectedMessage = new PmConfigurationUpdatedBrokerMessage(
                TestConstants.UUID_LIST.get(0),
                TestConstants.NOW,
                new PmConfigurationUpdatedPayload(
                        TestConstants.CONNECTED_PM_ID,
                        audioActivation != AlertActivation.OFF,
                        audioActivation == AlertActivation.PSD));
        kafkaProducerMock.verifyMessageSent(
                settings.KAFKA_TOPIC_DEVICE(), TestConstants.CONNECTED_PM_ID, expectedMessage, null);
    }

    private void configureEhrApi(List<EhrPatient> ehrPatients) throws ApiRequestException {
        var ehrApi = injector.getInstance(EhrApi.class);
        reset(ehrApi);
        when(ehrApi.searchPatients(any())).thenReturn(ehrPatients);
    }

    // TODO: MAYBE MOVE THE SET MDIB ACCESS SOMEWHERE ELSE

    private ComponentStateModificationMessage createComponentStateModificationMessage(
            SensorType sensorType,
            String devicePrimaryIdentifier,
            BigDecimal remainingBattery,
            BatteryState.ChargeStatus chargeStatus)
            throws PreprocessingException {
        var mdibAccess = new MdibAccessBuilder()
                .addBattery(sensorType, devicePrimaryIdentifier, remainingBattery, chargeStatus)
                .build();
        setConnectedPmMdibAccess(mdibAccess);
        var batteryState = createBatteryState(sensorType, remainingBattery, chargeStatus);
        return new ComponentStateModificationMessage(mdibAccess, Map.of("key", List.of(batteryState)));
    }

    private MetricStateModificationMessage createMetricChangeModificationMessage(
            String devicePrimaryIdentifier, Metric metric, Object metricValue, MeasurementValidity validity)
            throws PreprocessingException {
        var mdibAccessBuilder = new MdibAccessBuilder()
                .addDevice(SensorType.ANNE_CHEST, devicePrimaryIdentifier)
                .addMetricChannel(SensorType.ANNE_CHEST, MetricChannel.VITALS);

        AbstractMetricState deviceMetricState = null;
        if (metricValue instanceof BigDecimal) {
            mdibAccessBuilder = mdibAccessBuilder.addMetric(
                    SensorType.ANNE_CHEST, metric, (BigDecimal) metricValue, METRIC_DETERMINATION_TIME);
            deviceMetricState = createNumericMetricState(
                    SensorType.ANNE_CHEST, metric, (BigDecimal) metricValue, METRIC_DETERMINATION_TIME, validity);
        } else if (metricValue instanceof String) {
            mdibAccessBuilder = mdibAccessBuilder.addMetric(
                    SensorType.ANNE_CHEST, metric, (String) metricValue, METRIC_DETERMINATION_TIME);
            deviceMetricState = createStringMetricState(
                    SensorType.ANNE_CHEST, metric, (String) metricValue, METRIC_DETERMINATION_TIME, validity);
        } else {
            fail(String.format(
                    "Unrecognized metric state type: %s", metricValue.getClass().getName()));
        }

        var mdibAccess = mdibAccessBuilder.build();
        setConnectedPmMdibAccess(mdibAccess);
        return new MetricStateModificationMessage(mdibAccess, Map.of("key", List.of(deviceMetricState)));
    }

    private WaveformStateModificationMessage createWaveformChangeModificationMessage(
            String devicePrimaryIdentifier,
            Metric metric,
            Duration samplePeriod,
            Duration determinationPeriod,
            Instant determinationTime)
            throws PreprocessingException {
        var mdibAccess = new MdibAccessBuilder()
                .addDevice(SensorType.ANNE_CHEST, devicePrimaryIdentifier)
                .addMetricChannel(SensorType.ANNE_CHEST, MetricChannel.VITALS)
                .addRealTimeMetric(
                        SensorType.ANNE_CHEST,
                        metric,
                        WAVEFORM_SAMPLE,
                        samplePeriod,
                        determinationPeriod,
                        determinationTime)
                .build();
        setConnectedPmMdibAccess(mdibAccess);
        var realTimeMetricState =
                createRealTimeMetricState(SensorType.ANNE_CHEST, metric, WAVEFORM_SAMPLE, determinationTime);
        return new WaveformStateModificationMessage(mdibAccess, Map.of("key", List.of(realTimeMetricState)));
    }

    private AlertStateModificationMessage createAlertChangeModificationMessage(
            SensorType sensorType,
            String devicePrimaryIdentifier,
            TechnicalAlert alert,
            boolean enabled,
            boolean withSources,
            boolean withDeterminationTime)
            throws PreprocessingException {
        var mdibAccess = new MdibAccessBuilder()
                .addDevice(sensorType, devicePrimaryIdentifier)
                .addMetricChannel(sensorType, MetricChannel.DEVICE)
                .addMetric(sensorType, alert.metric, BigDecimal.ZERO, METRIC_DETERMINATION_TIME)
                .addAlertSystem(SensorType.ANNE_CHEST)
                .addAlert(
                        sensorType,
                        alert,
                        enabled,
                        withDeterminationTime ? ALERT_DETERMINATION_TIME : null,
                        withSources)
                .build();
        setConnectedPmMdibAccess(mdibAccess);
        var alertState = createAlertState(sensorType, alert, enabled, false);
        return new AlertStateModificationMessage(mdibAccess, Map.of("key", List.of(alertState)));
    }

    private AlertStateModificationMessage createAlertChangeModificationMessage(
            SensorType sensorType, String devicePrimaryIdentifier, PhysiologicalAlert alert, boolean enabled)
            throws PreprocessingException {
        var mdibAccess = createMdibAccessWithPhysiologicalAlerts(
                sensorType, devicePrimaryIdentifier, List.of(alert), enabled, false);
        setConnectedPmMdibAccess(mdibAccess);
        var alertState = createAlertState(alert, enabled, false);
        return new AlertStateModificationMessage(mdibAccess, Map.of("key", List.of(alertState)));
    }

    private AlertStateModificationMessage createAlertChangeModificationMessage(
            SensorType sensorType,
            String devicePrimaryIdentifier,
            PhysiologicalAlert alert,
            boolean enabled,
            boolean latching)
            throws PreprocessingException {
        var mdibAccess = createMdibAccessWithPhysiologicalAlerts(
                sensorType, devicePrimaryIdentifier, List.of(alert), enabled, latching);
        setConnectedPmMdibAccess(mdibAccess);
        var alertState = createAlertState(alert, enabled, latching);
        return new AlertStateModificationMessage(mdibAccess, Map.of("key", List.of(alertState)));
    }

    private AlertStateModificationMessage createLimitAlertChangeModificationMessage(
            SensorType sensorType, String devicePrimaryIdentifier, List<PhysiologicalAlert> alerts)
            throws PreprocessingException {
        var mdibAccess =
                createMdibAccessWithPhysiologicalAlerts(sensorType, devicePrimaryIdentifier, alerts, false, false);
        setConnectedPmMdibAccess(mdibAccess);
        var alertConditionStates = alerts.stream()
                .map(MdibStateFactory::createAlertConditionState)
                .map(alert -> (AbstractAlertState) alert)
                .toList();
        return new AlertStateModificationMessage(mdibAccess, Map.of("key", alertConditionStates));
    }

    @SuppressWarnings("OptionalGetWithoutIsPresent")
    private DescriptionModificationMessage createPatientModificationMessage(
            PatientPayload patientPayload, DescriptionModificationMessageType descriptionModificationMessageType)
            throws PreprocessingException {
        var mdibWithPatient = createMdibWithPatient(patientPayload);
        var mdibWithoutPatient = new MdibAccessBuilder()
                .addSco(SensorType.PM)
                .addScoOperation(SensorType.PM, ScoOperationType.SET_CONTEXT_STATE)
                .build();
        var patientEntity =
                mdibWithPatient.getEntity(MdibHandles.PATIENT_CONTEXT_HANDLE).get();
        var patientDescriptor = patientEntity.getDescriptor();
        if (patientPayload.getAssociation() == ContextAssociation.NO) {
            // Needed as states with context association NO are deleted from the MDIB
            patientEntity = mock();
            when(patientEntity.getDescriptor()).thenReturn(patientDescriptor);
            var patientContextStates = List.of(createPatientContextState(
                    patientPayload.getPrimaryIdentifier(),
                    patientPayload.getGivenName(),
                    patientPayload.getFamilyName(),
                    patientPayload.getBirthDate(),
                    patientPayload.getGender(),
                    patientPayload.getAssociation(),
                    patientPayload.getValidators()));
            when(patientEntity.getStates())
                    .thenReturn(patientContextStates.stream()
                            .map(state -> (AbstractState) state)
                            .toList());
            when(patientEntity.getStates(PatientContextState.class)).thenReturn(patientContextStates);
        }

        List<MdibEntity> insertedEntities = List.of();
        List<MdibEntity> updatedEntities = List.of();
        List<MdibEntity> deletedEntities = List.of();
        switch (descriptionModificationMessageType) {
            case CREATE -> insertedEntities = List.of(patientEntity);
            case UPDATE -> updatedEntities = List.of(patientEntity);
            case DELETE -> deletedEntities = List.of(patientEntity);
        }

        var currentPmMdib = descriptionModificationMessageType != DescriptionModificationMessageType.DELETE
                ? mdibWithPatient
                : mdibWithoutPatient;
        setConnectedPmMdibAccess(currentPmMdib);
        return new DescriptionModificationMessage(currentPmMdib, insertedEntities, updatedEntities, deletedEntities);
    }

    @SuppressWarnings("OptionalGetWithoutIsPresent")
    private DescriptionModificationMessage createDeletedSensorModificationMessage(String devicePrimaryIdentifier)
            throws PreprocessingException {
        var mdibWithDevice = new MdibAccessBuilder()
                .addDevice(SensorType.ANNE_CHEST, devicePrimaryIdentifier)
                .build();
        var mdibWithoutDevice = new MdibAccessBuilder().build();
        var deviceEntity = mdibWithDevice
                .getEntity(MdibHandles.getDeviceHandle(SensorType.ANNE_CHEST))
                .get();
        setConnectedPmMdibAccess(mdibWithoutDevice);
        return new DescriptionModificationMessage(mdibWithoutDevice, List.of(), List.of(), List.of(deviceEntity));
    }

    @SuppressWarnings("OptionalGetWithoutIsPresent")
    private DescriptionModificationMessage createUpdatedSensorModificationMessage() throws PreprocessingException {
        var mdibAccess = new MdibAccessBuilder()
                .addDevice(SensorType.ANNE_CHEST, ANNE_CHEST_ID)
                .addAlertSystem(SensorType.ANNE_CHEST)
                .build();
        setConnectedPmMdibAccess(mdibAccess);
        var deviceEntity = mdibAccess.getEntity(MdibHandles.ROOT_HANDLE).get();
        return new DescriptionModificationMessage(mdibAccess, List.of(), List.of(deviceEntity), List.of());
    }

    @SuppressWarnings("OptionalGetWithoutIsPresent")
    private DescriptionModificationMessage createLimitDescriptionModificationMessage(List<PhysiologicalAlert> alerts)
            throws PreprocessingException {
        var mdibAccess =
                createMdibAccessWithPhysiologicalAlerts(SensorType.ANNE_CHEST, ANNE_CHEST_ID, alerts, false, false);
        setConnectedPmMdibAccess(mdibAccess);
        var deviceEntities = alerts.stream()
                .map(MdibHandles::getAlertConditionHandle)
                .map(alertHandle -> mdibAccess.getEntity(alertHandle).get())
                .toList();
        return new DescriptionModificationMessage(mdibAccess, List.of(), deviceEntities, List.of());
    }

    private AlertStateModificationMessage createAlertSystemModificationMessage(AlertActivation audioActivation)
            throws PreprocessingException {
        var mdibAccess = new MdibAccessBuilder()
                .addAlertSystem(SensorType.PM, audioActivation)
                .build();
        setConnectedPmMdibAccess(mdibAccess);
        return new AlertStateModificationMessage(
                mdibAccess, Map.of("key", List.of(createAlertSystemState(SensorType.PM, audioActivation))));
    }

    private static MdibAccess createMdibAccessWithPhysiologicalAlerts(
            SensorType sensorType,
            String devicePrimaryIdentifier,
            List<PhysiologicalAlert> alerts,
            boolean enabled,
            boolean latching)
            throws PreprocessingException {
        var mdibAccessBuilder = new MdibAccessBuilder()
                .addDevice(sensorType, devicePrimaryIdentifier)
                .addMetricChannel(sensorType, MetricChannel.VITALS)
                .addAlertSystem(SensorType.PM);
        for (var alert : alerts) {
            mdibAccessBuilder.addAlert(alert, enabled, ALERT_DETERMINATION_TIME, latching);
            for (var source : alert.condition.sources) {
                mdibAccessBuilder.addMetric(sensorType, source.metric(), BigDecimal.ZERO, METRIC_DETERMINATION_TIME);
            }
        }

        return mdibAccessBuilder.build();
    }

    private static LocalMdibAccess createMdibWithPatient(PatientPayload patientPayload) throws PreprocessingException {
        return new MdibAccessBuilder()
                .addSco(SensorType.PM)
                .addScoOperation(SensorType.PM, ScoOperationType.SET_CONTEXT_STATE)
                .addPatient(
                        patientPayload.getPrimaryIdentifier(),
                        patientPayload.getGivenName(),
                        patientPayload.getFamilyName(),
                        patientPayload.getBirthDate(),
                        patientPayload.getGender(),
                        patientPayload.getAssociation(),
                        patientPayload.getValidators())
                .build();
    }
}
