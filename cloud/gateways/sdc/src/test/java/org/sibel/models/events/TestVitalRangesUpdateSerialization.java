package org.sibel.models.events;

import java.math.BigDecimal;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.sibel.TestConstants;
import org.sibel.models.SerializationTest;
import org.sibel.models.VitalRange;

public class TestVitalRangesUpdateSerialization extends SerializationTest {
    @Test
    public void testSerialization() {
        assertObjectSerialized(
                new VitalRangesUpdateEvent(
                        TestConstants.UUID_LIST.getFirst(),
                        TestConstants.NOW,
                        TestConstants.CONNECTED_PM_ID,
                        TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                        List.of(
                                new VitalRange("12345", BigDecimal.ZERO, BigDecimal.ONE),
                                new VitalRange("54321", BigDecimal.ONE, BigDecimal.TWO))),
                """
                        {
                          "vital_ranges": [
                            {
                              "code": "12345",
                              "lower_limit": 0,
                              "upper_limit": 1
                            },
                            {
                              "code": "54321",
                              "lower_limit": 1,
                              "upper_limit": 2
                            }
                          ],
                          "event_type": "VITAL_RANGES_UPDATE",
                          "id": "43ac93b6-e4bc-4b90-aedd-f099906c5d6f",
                          "timestamp": "2023-10-31T08:00:00.000",
                          "pm_id": "PM-001",
                          "patient_id": "P-001"
                        }""");
    }
}
