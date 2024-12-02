package org.sibel.models.events;

import java.util.List;
import org.junit.jupiter.api.Test;
import org.sibel.TestConstants;
import org.sibel.constants.SensorType;
import org.sibel.models.Sensor;
import org.sibel.models.SerializationTest;

public class TestSensorsUpdateSerialization extends SerializationTest {
    @Test
    public void testSerialization() {
        assertObjectSerialized(
                new SensorsUpdateEvent(
                        TestConstants.UUID_LIST.getFirst(),
                        TestConstants.NOW,
                        TestConstants.CONNECTED_PM_ID,
                        TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                        List.of(
                                new Sensor("S-0001", SensorType.ANNE_CHEST),
                                new Sensor("S-0002", SensorType.ANNE_LIMB))),
                """
                        {
                          "connected_sensors": [
                            {
                              "id": "S-0001",
                              "type": "ANNE Chest"
                            },
                            {
                              "id": "S-0002",
                              "type": "ANNE Limb"
                            }
                          ],
                          "event_type": "SENSORS_UPDATE",
                          "id": "43ac93b6-e4bc-4b90-aedd-f099906c5d6f",
                          "timestamp": "2023-10-31T08:00:00.000",
                          "pm_id": "PM-001",
                          "patient_id": "P-001"
                        }""");
    }
}
