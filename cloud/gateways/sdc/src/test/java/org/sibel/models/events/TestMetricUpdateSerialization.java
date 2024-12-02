package org.sibel.models.events;

import java.math.BigDecimal;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.sibel.TestConstants;
import org.sibel.constants.SensorType;
import org.sibel.constants.UnitCodes;
import org.sibel.models.MetricUpdate;
import org.sibel.models.Sensor;
import org.sibel.models.SerializationTest;

public class TestMetricUpdateSerialization extends SerializationTest {
    @Test
    public void testSerialization() {
        assertObjectSerialized(
                new MetricsUpdateEvent<>(
                        TestConstants.UUID_LIST.getFirst(),
                        TestConstants.NOW,
                        TestConstants.CONNECTED_PM_ID,
                        TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                        List.of(new MetricUpdate<>(
                                "12345",
                                new Sensor("S-0001", SensorType.ANNE_CHEST),
                                BigDecimal.ONE,
                                UnitCodes.PERCENTAGE,
                                TestConstants.METRIC_DETERMINATION_TIME))),
                """
                        {
                          "metric_updates": [
                            {
                              "code": "12345",
                              "sensor": {
                                "id": "S-0001",
                                "type": "ANNE Chest"
                              },
                              "value": 1,
                              "unit_code": "262688",
                              "determination_time": "2023-10-31T08:30:00.000"
                            }
                          ],
                          "event_type": "METRICS_UPDATE",
                          "id": "43ac93b6-e4bc-4b90-aedd-f099906c5d6f",
                          "timestamp": "2023-10-31T08:00:00.000",
                          "pm_id": "PM-001",
                          "patient_id": "P-001"
                        }""");
    }
}
