package org.sibel;

import static org.sibel.mdib.MdibStateFactory.createPatientContextState;

import java.time.Instant;
import java.util.List;
import java.util.Set;
import org.sibel.models.payloads.internal.PatientPayload;
import org.somda.sdc.biceps.model.participant.ContextAssociation;
import org.somda.sdc.biceps.model.participant.PatientContextState;
import org.somda.sdc.biceps.model.participant.Sex;
import org.somda.sdc.dpws.client.DiscoveredDevice;

public class TestConstants {
    public static final String CONSUMER_ID = "TEST_CONSUMER_ID";
    public static final String CONNECTED_PM_ID = "PM-001";
    public static final String DISCONNECTED_PM_ID = "PM-002";

    @SuppressWarnings("PMD.AvoidUsingHardCodedIP")
    public static final String CONNECTED_PM_EPR = "198.168.0.1";

    public static final DiscoveredDevice CONNECTED_PM_DISCOVERED_DEVICE =
            new DiscoveredDevice(CONNECTED_PM_EPR, List.of(), List.of(), List.of(), 0);
    public static final PatientPayload CONNECTED_PATIENT = new PatientPayload(
            "P-001",
            "John",
            "Smith",
            "01-01-1980",
            Sex.M,
            ContextAssociation.ASSOC,
            Set.of(Settings.CENTRAL_HUB_VALIDATOR_ID, Settings.PATIENT_MONITOR_VALIDATOR_ID));
    public static final PatientPayload CONNECTED_PATIENT_REJECTED = new PatientPayload(
            CONNECTED_PATIENT.getPrimaryIdentifier(),
            CONNECTED_PATIENT.getGivenName(),
            CONNECTED_PATIENT.getFamilyName(),
            CONNECTED_PATIENT.getBirthDate(),
            CONNECTED_PATIENT.getGender(),
            ContextAssociation.NO,
            Set.of(Settings.CENTRAL_HUB_VALIDATOR_ID));
    public static final PatientContextState CONNECTED_PATIENT_CONTEXT_REJECTED = createPatientContextState(
            CONNECTED_PATIENT_REJECTED.getPrimaryIdentifier(),
            CONNECTED_PATIENT_REJECTED.getGivenName(),
            CONNECTED_PATIENT_REJECTED.getFamilyName(),
            CONNECTED_PATIENT_REJECTED.getBirthDate(),
            CONNECTED_PATIENT_REJECTED.getGender(),
            CONNECTED_PATIENT_REJECTED.getAssociation(),
            CONNECTED_PATIENT_REJECTED.getValidators());

    public static final List<String> UUID_LIST = List.of(
            "43ac93b6-e4bc-4b90-aedd-f099906c5d6f",
            "1bfff845-5524-4e8e-a0e2-959615595099",
            "fa0a89ca-c3eb-439b-955d-21a83e3e53ef",
            "df59041b-bdca-411b-808c-1e2f8403abb0",
            "bcd2b099-1cc4-45f9-902e-b5d2fac4ce9f");

    public static final Instant NOW = Instant.parse("2023-10-31T08:00:00Z");
    public static final Instant METRIC_DETERMINATION_TIME = Instant.parse("2023-10-31T08:30:00Z");

    public static class Settings {
        public static final String DEVICE_KAFKA_TOPIC = "device-kafka-topic";
        public static final String VITALS_KAFKA_TOPIC = "vitals-kafka-topic";
        public static final String ALERTS_KAFKA_TOPIC = "alerts-kafka-topic";
        public static final String COMMANDS_RESPONSE_KAFKA_TOPIC = "commands-response-kafka-topic";
        public static final boolean DETERMINATION_PERIOD_ENABLED = true;
        public static final String CENTRAL_HUB_VALIDATOR_ID = "CMS";
        public static final String PATIENT_MONITOR_VALIDATOR_ID = "PM";
    }
}
