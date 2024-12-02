package org.sibel.tasks;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

import java.util.Collection;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.mockito.ArgumentCaptor;
import org.sibel.BaseIntegrationTest;
import org.sibel.TestConstants;
import org.sibel.constants.ScoOperationType;
import org.sibel.constants.SensorType;
import org.sibel.mdib.MdibAccessBuilder;
import org.sibel.mdib.mdpws.SelectorType;
import org.sibel.models.payloads.internal.PatientPayload;
import org.somda.sdc.biceps.common.storage.PreprocessingException;
import org.somda.sdc.biceps.model.message.*;
import org.somda.sdc.biceps.model.participant.PatientContextState;
import org.somda.sdc.biceps.model.participant.Sex;

class TestKafkaConsumerTask extends BaseIntegrationTest {
    private final KafkaConsumerTask task;

    private final PatientPayload patientPayload =
            new PatientPayload("jdoe", "John", "Doe", "1992-06-01", Sex.M, null, null);

    public TestKafkaConsumerTask() {
        task = injector.getInstance(KafkaConsumerTask.class);
    }

    @BeforeEach
    void setUp() throws PreprocessingException {
        configureDefaultMocks();

        configurePatientMonitorMdibAccess(null);
    }

    @Test
    void testWronglyFormattedMessage() {
        task.handleBrokerMessageReceived("{\"fake\": \"json\"}");

        verifySetPatientContextNotCalled();
    }

    @Test
    void testPatientEncounterPlannedReceived() {
        task.handleBrokerMessageReceived(createPatientEncounterMessage(TestConstants.CONNECTED_PM_ID, patientPayload));
        verifySetPatientContextCalled(patientPayload);
    }

    @Test
    void testPatientEncounterPlannedReceivedFailedToExecuteSco() {
        configureSetServiceAccessMock(false);

        task.handleBrokerMessageReceived(createPatientEncounterMessage(TestConstants.CONNECTED_PM_ID, patientPayload));

        verifySetPatientContextCalled(patientPayload);
        // TODO: Maybe send an error message here. But at least it should not fail with an exception.
    }

    @Test
    void testPatientEncounterPlannedReceivedDisconnectedPatientMonitor() {
        task.handleBrokerMessageReceived(createPatientEncounterMessage("PM-DISCONNECTED-001", patientPayload));

        verifySetPatientContextNotCalled();
    }

    /**
     * Tests IEEE 11073 SDC 20701-R0066
     *
     * Description:
     *      If an mdpws:SafetyContextDef does not reference one of the MDIB VERSIONING ATTRIBUTEs then an
     *      SDC SERVICE CONSUMER SHALL ensure that OPERATOR awareness of the content of each defined
     *      mdpws:SafetyContextDef ELEMENT of a pm:AbstractOperationDescriptor is achieved before
     *      remote-control command invocation of that operation.
     */
    @ParameterizedTest
    @ValueSource(
            strings = {
                "This must be a valid XPath and most point to an MDIB versioning attribute",
                "/Valid/Xpath/But/Invalid/Element"
            })
    void testPatientEncounterPlannedReceivedInvalidScoSafetyReq(String safetyReqSelector)
            throws PreprocessingException {
        // With set patient SCO with safety requirements and a patient with no data
        var scoSafetyReqDefinition = new SelectorType();
        scoSafetyReqDefinition.setId("some random id");
        scoSafetyReqDefinition.setValue(safetyReqSelector);

        configurePatientMonitorMdibAccess(List.of(scoSafetyReqDefinition));

        task.handleBrokerMessageReceived(createPatientEncounterMessage(TestConstants.CONNECTED_PM_ID, patientPayload));

        verifySetPatientContextNotCalled();
    }

    private void verifySetPatientContextNotCalled() {
        verify(setServiceAccessMock, never()).invoke(any(), eq(SetContextStateResponse.class));
    }

    private void verifySetPatientContextCalled(PatientPayload patientPayload) {
        var captor = ArgumentCaptor.forClass(SetContextState.class);
        verify(setServiceAccessMock).invoke(captor.capture(), eq(SetContextStateResponse.class));

        var setPatientContext = captor.getValue();
        var patientContext = (PatientContextState)
                setPatientContext.getProposedContextState().get(0);
        assertEquals(
                patientPayload.getPrimaryIdentifier(),
                patientContext.getIdentification().get(0).getExtensionName());
        assertEquals(patientPayload.getGivenName(), patientContext.getCoreData().getGivenname());
        assertEquals(
                patientPayload.getFamilyName(), patientContext.getCoreData().getFamilyname());
        assertEquals(patientPayload.getBirthDate(), patientContext.getCoreData().getDateOfBirth());
        assertEquals(patientPayload.getGender(), patientContext.getCoreData().getSex());
    }

    private void configurePatientMonitorMdibAccess(Collection<SelectorType> safetyReqDefElements)
            throws PreprocessingException {
        var mdibAccess = new MdibAccessBuilder()
                .addDevice(SensorType.ANNE_CHEST, "ANNE-CHEST-001")
                .addSco(SensorType.ANNE_CHEST)
                .addScoOperation(SensorType.ANNE_CHEST, ScoOperationType.SET_CONTEXT_STATE, safetyReqDefElements)
                .build();
        setConnectedPmMdibAccess(mdibAccess);
    }

    private static String createPatientEncounterMessage(String pmId, PatientPayload patientPayload) {
        return """
                {
                    "entity_id":"d03119c2-aa1e-486a-abbb-cc8d4d696fb6",
                    "event_name":"Patient admission planned",
                    "performed_on":"2024-07-01T19:00:00.000Z",
                    "performed_by":"b4f6f4e0-6ca5-4be9-99d4-28d66bd82ecd",
                    "event_state":{
                        "id":"d03119c2-aa1e-486a-abbb-cc8d4d696fb6",
                        "status":"planned",
                        "created_at":"2024-07-01T19:00:00.000Z",
                        "start_time":"None",
                        "end_time":"None",
                        "device":{
                            "id":"1db9441c-e4fb-453c-a4d5-5d05c1f3f484",
                            "primary_identifier":"%s",
                            "name":"lHIssGJPEDcpbLYivGcM",
                            "location_id":"67cbea05-c48a-4ec2-9ce5-fa4d5518dfa5",
                            "gateway_id":"None",
                            "audio_pause_enabled":true,
                            "audio_enabled":false
                        },
                        "patient":{
                            "id":"d03119c2-aa1e-486a-abbb-cc8d4d696fb6",
                            "primary_identifier":"%s",
                            "active":false,
                            "given_name":"%s",
                            "family_name":"%s",
                            "gender":"%s",
                            "birth_date":"%s"
                        }
                    },
                    "previous_state":{},
                    "event_type":"PATIENT_ENCOUNTER_PLANNED",
                    "message_id":"d03119c2-aa1e-486a-abbb-cc8d4d696fb6",
                    "event_data":{},
                    "entity_name":"patient",
                    "emitted_by":"patient"
                }"""
                .formatted(
                        pmId,
                        patientPayload.getPrimaryIdentifier(),
                        patientPayload.getGivenName(),
                        patientPayload.getFamilyName(),
                        patientPayload.getGenderText(),
                        patientPayload.getBirthDate());
    }
}
