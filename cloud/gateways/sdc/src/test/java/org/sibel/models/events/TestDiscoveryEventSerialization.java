package org.sibel.models.events;

import java.math.BigDecimal;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.sibel.TestConstants;
import org.sibel.constants.SensorType;
import org.sibel.models.*;

public class TestDiscoveryEventSerialization extends SerializationTest {
    @Test
    public void testSerialization() {
        assertObjectSerialized(
                new DiscoveryEvent(
                        TestConstants.UUID_LIST.getFirst(),
                        TestConstants.NOW,
                        TestConstants.CONNECTED_PM_ID,
                        TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                        new Patient("John", "Doe", Gender.MALE, "1995-01-01"),
                        List.of(
                                new Sensor("S-0001", SensorType.ANNE_CHEST),
                                new Sensor("S-0002", SensorType.ANNE_LIMB)),
                        List.of(
                                new VitalRange("12345", BigDecimal.ZERO, BigDecimal.ONE),
                                new VitalRange("54321", BigDecimal.ONE, BigDecimal.TWO)),
                        List.of(new Alert(
                                AlertType.PHYSIOLOGICAL,
                                "12345",
                                new Sensor("S-0001", SensorType.ANNE_CHEST),
                                AlertPriority.HI,
                                true,
                                true,
                                TestConstants.METRIC_DETERMINATION_TIME,
                                new VitalRange("11111", BigDecimal.ZERO, BigDecimal.ONE)))),
                """
                        {
                          "patient": {
                            "given_name": "John",
                            "family_name": "Doe",
                            "gender": "male",
                            "birth_date": "1995-01-01"
                          },
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
                          "alerts": [
                            {
                              "type": "PHYSIOLOGICAL",
                              "code": "12345",
                              "sensor": {
                                "id": "S-0001",
                                "type": "ANNE Chest"
                              },
                              "priority": "HI",
                              "active": true,
                              "latching": true,
                              "determination_time": "2023-10-31T08:30:00.000",
                              "vital_range": {
                                "code": "11111",
                                "lower_limit": 0,
                                "upper_limit": 1
                              }
                            }
                          ],
                          "event_type": "DISCOVERY",
                          "id": "43ac93b6-e4bc-4b90-aedd-f099906c5d6f",
                          "timestamp": "2023-10-31T08:00:00.000",
                          "pm_id": "PM-001",
                          "patient_id": "P-001"
                        }""");
    }
}
