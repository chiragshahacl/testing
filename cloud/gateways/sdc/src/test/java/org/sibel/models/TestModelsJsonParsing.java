package org.sibel.models;

import com.google.common.primitives.Ints;
import java.math.BigDecimal;
import java.time.Duration;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Stream;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.sibel.models.payloads.AlertPayload;
import org.sibel.models.payloads.MetricPayload;
import org.sibel.models.payloads.WaveformPayload;
import org.sibel.models.scoParams.SetPatientContextParams;
import org.somda.sdc.biceps.model.participant.ContextAssociation;
import org.somda.sdc.biceps.model.participant.Sex;

public class TestModelsJsonParsing extends SerializationTest {
    public static Stream<Arguments> testSerialization() {
        return Stream.of(
                Arguments.arguments(
                        new AlertBrokerMessage(
                                "498cf28c-0014-4609-8b27-1e61a55cdf77",
                                Instant.parse("2024-04-02T13:39:31.14Z"),
                                new AlertPayload(
                                        "P-001",
                                        true,
                                        false,
                                        "65000",
                                        "ANNE Chest",
                                        "ME",
                                        Instant.parse("2024-04-02T12:30:00Z"),
                                        "SEM-001",
                                        null)),
                        """
                        {
                          "message_id": "498cf28c-0014-4609-8b27-1e61a55cdf77",
                          "event_name": "Alert update",
                          "event_type": "NEW_ALERT_OBSERVATION",
                          "timestamp": "2024-04-02T13:39:31.140",
                          "payload": {
                            "patient_primary_identifier": "P-001",
                            "patient_id": "P-001",
                            "active": true,
                            "latching": false,
                            "code": "65000",
                            "device_code": "ANNE Chest",
                            "priority": "ME",
                            "determination_time": "2024-04-02T12:30:00.000",
                            "device_primary_identifier": "SEM-001"
                          }
                        }"""),
                Arguments.arguments(
                        new WaveformBrokerMessage(
                                "498cf28c-0014-4609-8b27-1e61a55cdf77",
                                Instant.parse("2024-04-02T13:39:31.14Z"),
                                new WaveformPayload(
                                        "P-001",
                                        Arrays.asList(new BigDecimal("1.0"), new BigDecimal("0.5")),
                                        Instant.parse("2024-04-02T13:39:31.14Z"),
                                        Duration.ofMillis(100),
                                        Duration.ofMillis(200),
                                        "131328",
                                        "ANNE Chest",
                                        "SEM-001")),
                        """
                        {
                          "message_id": "498cf28c-0014-4609-8b27-1e61a55cdf77",
                          "event_name": "New waveform vitals",
                          "event_type": "NEW_WAVEFORM_VITALS",
                          "timestamp": "2024-04-02T13:39:31.140",
                          "payload": {
                            "patient_id": "P-001",
                            "patient_primary_identifier": "P-001",
                            "samples": [
                              1.0,
                              0.5
                            ],
                            "determination_time": "2024-04-02T13:39:31.140",
                            "sample_period": "PT0.1S",
                            "determination_period": "PT0.2S",
                            "code": "131328",
                            "device_code": "ANNE Chest",
                            "device_primary_identifier": "SEM-001"
                          }
                        }"""),
                Arguments.arguments(
                        new MetricBrokerMessage<>(
                                "c8e7e082-ac8a-445e-9d2e-104379623a24",
                                Instant.parse("2024-04-11T14:12:21.67Z"),
                                new MetricPayload<>(
                                        "P-001",
                                        Ints.asList(45),
                                        Instant.parse("2024-04-02T12:30:00Z"),
                                        "147844",
                                        "264864",
                                        "ANNE Chest",
                                        "SEM-001")),
                        """
                        {
                          "message_id": "c8e7e082-ac8a-445e-9d2e-104379623a24",
                          "event_name": "New metrics found",
                          "event_type": "NEW_METRICS",
                          "timestamp": "2024-04-11T14:12:21.670",
                          "payload": {
                            "patient_id": "P-001",
                            "patient_primary_identifier": "P-001",
                            "samples": [
                              45
                            ],
                            "determination_time": "2024-04-02T12:30:00.000",
                            "code": "147844",
                            "device_code": "ANNE Chest",
                            "unit_code": "264864",
                            "device_primary_identifier": "SEM-001"
                          }
                        }"""),
                Arguments.arguments(
                        CommandExecutionResponseBrokerMessage.createSuccessResponse(
                                new CommandEventBrokerMessage(
                                        "entity_id",
                                        "event_name",
                                        "command_name",
                                        "pm_identifier",
                                        "request_id",
                                        Instant.parse("2024-04-11T10:00:00.00Z"),
                                        "performed_by",
                                        "entity_name",
                                        "emitted_by",
                                        "event_type",
                                        "message_id",
                                        "{}"),
                                Instant.parse("2024-04-11T10:00:01.00Z")),
                        """
                        {
                          "entity_id": "entity_id",
                          "event_name": "Command execution response",
                          "performed_on": "2024-04-11T10:00:01.000",
                          "performed_by": "performed_by",
                          "event_state": {
                            "success": true,
                            "errors": []
                          },
                          "previous_state": {},
                          "entity_name": "device",
                          "emitted_by": "sdc",
                          "event_type": "COMMAND_EXECUTION_RESPONSE",
                          "message_id": "message_id"
                        }"""),
                Arguments.arguments(
                        CommandExecutionResponseBrokerMessage.createErrorResponse(
                                List.of("error1", "error2", "error3", "error4"),
                                new CommandEventBrokerMessage(
                                        "entity_id",
                                        "event_name",
                                        "command_name",
                                        "pm_identifier",
                                        "request_id",
                                        Instant.parse("2024-04-11T10:00:00.00Z"),
                                        "performed_by",
                                        "entity_name",
                                        "emitted_by",
                                        "event_type",
                                        "message_id",
                                        "{}"),
                                Instant.parse("2024-04-11T10:00:01.00Z")),
                        """
                        {
                          "entity_id": "entity_id",
                          "event_name": "Command execution response",
                          "performed_on": "2024-04-11T10:00:01.000",
                          "performed_by": "performed_by",
                          "event_state": {
                            "success": false,
                            "errors": [
                              "error1",
                              "error2",
                              "error3",
                              "error4"
                            ]
                          },
                          "previous_state": {},
                          "entity_name": "device",
                          "emitted_by": "sdc",
                          "event_type": "COMMAND_EXECUTION_RESPONSE",
                          "message_id": "message_id"
                        }"""));
    }

    @ParameterizedTest
    @MethodSource
    void testSerialization(Object modelInstance, String expectedJson) {
        assertObjectSerialized(modelInstance, expectedJson);
    }

    public static Stream<Arguments> testDeserialization() {
        return Stream.of(
                Arguments.arguments(
                        """
                        {
                          "entity_id": "entity_id",
                          "event_name": "event_name",
                          "event_state": {
                            "command_name": "command_name",
                            "pm_identifier": "pm_identifier",
                            "request_id": "request_id",
                            "params": {
                              "primary_identifier": "jdoe",
                              "given_name": "John",
                              "family_name": "Doe",
                              "gender": "male",
                              "birth_date": "1992-06-01"
                            }
                          },
                          "performed_on": "2024-04-11T14:12:21.670",
                          "performed_by": "performed_by",
                          "entity_name": "entity_name",
                          "emitted_by": "emitted_by",
                          "event_type": "event_type",
                          "message_id": "message_id"
                        }""",
                        CommandEventBrokerMessage.class,
                        new CommandEventBrokerMessage(
                                "entity_id",
                                "event_name",
                                "command_name",
                                "pm_identifier",
                                "request_id",
                                Instant.parse("2024-04-11T14:12:21.67Z"),
                                "performed_by",
                                "entity_name",
                                "emitted_by",
                                "event_type",
                                "message_id",
                                "{\"primary_identifier\":\"jdoe\",\"given_name\":\"John\",\"family_name\":\"Doe\",\"gender\":\"male\",\"birth_date\":\"1992-06-01\"}")),
                Arguments.arguments(
                        """
                        {
                          "primary_identifier": "jdoe",
                          "given_name": "John",
                          "family_name": "Doe",
                          "gender": "male",
                          "birth_date": "1992-06-01"
                        }""",
                        SetPatientContextParams.class,
                        new SetPatientContextParams(List.of(new SetPatientContextParams.Patient(
                                "jdoe", "John", "Doe", Sex.M, "1992-06-01", ContextAssociation.ASSOC)))),
                Arguments.arguments(
                        """
                        {
                          "primary_identifier": "jndoe",
                          "given_name": "Jane",
                          "family_name": "Doe",
                          "gender": "female",
                          "birth_date": "1992-06-02"
                        }""",
                        SetPatientContextParams.class,
                        new SetPatientContextParams(List.of(new SetPatientContextParams.Patient(
                                "jndoe", "Jane", "Doe", Sex.F, "1992-06-02", ContextAssociation.ASSOC)))));
    }

    @ParameterizedTest
    @MethodSource
    void testDeserialization(String rawJson, Class<?> model, Object expectedModelInstance) {
        assertObjectDeserialized(expectedModelInstance, model, rawJson);
    }
}
