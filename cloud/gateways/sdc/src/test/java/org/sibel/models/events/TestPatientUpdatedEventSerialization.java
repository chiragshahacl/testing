package org.sibel.models.events;

import org.junit.jupiter.api.Test;
import org.sibel.TestConstants;
import org.sibel.models.Gender;
import org.sibel.models.Patient;
import org.sibel.models.SerializationTest;

public class TestPatientUpdatedEventSerialization extends SerializationTest {
    @Test
    public void testSerialization() {
        assertObjectSerialized(
                new PatientSessionStartedEvent(
                        TestConstants.UUID_LIST.getFirst(),
                        TestConstants.NOW,
                        TestConstants.CONNECTED_PM_ID,
                        TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                        new Patient("John", "Doe", Gender.MALE, "1995-01-01")),
                """
                        {
                          "patient": {
                            "given_name": "John",
                            "family_name": "Doe",
                            "gender": "male",
                            "birth_date": "1995-01-01"
                          },
                          "event_type": "PATIENT_SESSION_STARTED",
                          "id": "43ac93b6-e4bc-4b90-aedd-f099906c5d6f",
                          "timestamp": "2023-10-31T08:00:00.000",
                          "pm_id": "PM-001",
                          "patient_id": "P-001"
                        }""");
    }
}
