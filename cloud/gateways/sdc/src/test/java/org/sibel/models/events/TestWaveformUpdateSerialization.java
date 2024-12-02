package org.sibel.models.events;

import java.math.BigDecimal;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.sibel.TestConstants;
import org.sibel.constants.SensorType;
import org.sibel.constants.UnitCodes;
import org.sibel.models.Sensor;
import org.sibel.models.SerializationTest;
import org.sibel.models.WaveformUpdate;

public class TestWaveformUpdateSerialization extends SerializationTest {
    @Test
    public void testSerialization() {
        assertObjectSerialized(
                new WaveformsUpdateEvent(
                        TestConstants.UUID_LIST.getFirst(),
                        TestConstants.NOW,
                        TestConstants.CONNECTED_PM_ID,
                        TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier(),
                        List.of(new WaveformUpdate(
                                "12345",
                                new Sensor("S-0001", SensorType.ANNE_CHEST),
                                List.of(BigDecimal.ZERO, BigDecimal.ONE, BigDecimal.TWO),
                                UnitCodes.BEATS_PER_MINUTE,
                                TestConstants.METRIC_DETERMINATION_TIME,
                                "PT0.50000000S",
                                "PT1.00000000S"))),
                """
                        {
                          "waveform_updates": [
                            {
                              "code": "12345",
                              "sensor": {
                                "id": "S-0001",
                                "type": "ANNE Chest"
                              },
                              "samples": [
                                0,
                                1,
                                2
                              ],
                              "unit_code": "264864",
                              "determination_time": "2023-10-31T08:30:00.000",
                              "determination_period": "PT0.50000000S",
                              "sample_period": "PT1.00000000S"
                            }
                          ],
                          "event_type": "WAVEFORMS_UPDATE",
                          "id": "43ac93b6-e4bc-4b90-aedd-f099906c5d6f",
                          "timestamp": "2023-10-31T08:00:00.000",
                          "pm_id": "PM-001",
                          "patient_id": "P-001"
                        }""");
    }
}
