package org.sibel.emulator;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

import java.time.Instant;
import java.util.List;
import java.util.Random;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.sibel.constants.MdibHandles;
import org.sibel.constants.Metric;
import org.sibel.constants.MetricChannel;
import org.sibel.constants.SensorType;
import org.sibel.emulator.metrics.EnumStringMetricEmulator;
import org.sibel.mdib.MdibAccessBuilder;
import org.somda.sdc.biceps.common.storage.PreprocessingException;
import org.somda.sdc.biceps.model.participant.StringMetricState;
import org.somda.sdc.biceps.provider.access.LocalMdibAccess;

class TestEnumStringMetricEmulator {
    private final Random mockRandom = mock();
    private LocalMdibAccess mdibAccess;

    @BeforeEach
    void setUp() throws PreprocessingException {

        reset(mockRandom);

        mdibAccess = new MdibAccessBuilder()
                .addDevice(SensorType.ANNE_CHEST, "SEM-0001")
                .addMetricChannel(SensorType.ANNE_CHEST, MetricChannel.VITALS)
                .addMetric(SensorType.ANNE_CHEST, Metric.BODY_POSITION, "another_value", Instant.now())
                .build();
    }

    @Test
    void testNextState() {
        var emulator = new EnumStringMetricEmulator(
                mockRandom,
                mdibAccess,
                SensorType.ANNE_CHEST,
                Metric.BODY_POSITION,
                List.of("value_1", "value_2", "value_3"),
                100);

        when(mockRandom.nextInt(3)).thenReturn(0);
        emulator.writeNextMetric();
        assertPosition("value_1");

        when(mockRandom.nextInt(3)).thenReturn(1);
        emulator.writeNextMetric();
        assertPosition("value_2");

        when(mockRandom.nextInt(3)).thenReturn(2);
        emulator.writeNextMetric();
        assertPosition("value_3");
    }

    private void assertPosition(String expectedPosition) {
        var metricHandle = MdibHandles.getMetricHandle(SensorType.ANNE_CHEST, Metric.BODY_POSITION);
        var state = (StringMetricState) mdibAccess.getState(metricHandle).orElseThrow();
        assertEquals(expectedPosition, state.getMetricValue().getValue());
    }
}
