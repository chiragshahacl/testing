package org.sibel.models.events;

import org.junit.jupiter.api.Test;
import org.sibel.TestConstants;
import org.sibel.models.SerializationTest;

public class TestHealthCheckEventSerialization extends SerializationTest {
    @Test
    public void testSerialization() {
        assertObjectSerialized(
                new HealthCheckEvent(
                        TestConstants.UUID_LIST.getFirst(),
                        TestConstants.NOW,
                        TestConstants.CONNECTED_PM_ID,
                        TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier()),
                """
                        {
                          "event_type": "HEALTH_CHECK",
                          "id": "43ac93b6-e4bc-4b90-aedd-f099906c5d6f",
                          "timestamp": "2023-10-31T08:00:00.000",
                          "pm_id": "PM-001",
                          "patient_id": "P-001"
                        }""");
    }
}
