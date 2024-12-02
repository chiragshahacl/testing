package org.sibel.emulator;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.*;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.Random;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.sibel.constants.MdibHandles;
import org.sibel.constants.Metric;
import org.sibel.constants.MetricChannel;
import org.sibel.constants.SensorType;
import org.sibel.emulator.metrics.NumericMetricEmulator;
import org.sibel.mdib.MdibAccessBuilder;
import org.somda.sdc.biceps.common.storage.PreprocessingException;
import org.somda.sdc.biceps.model.participant.NumericMetricState;
import org.somda.sdc.biceps.provider.access.LocalMdibAccess;

class TestNumericMetricEmulator {
    private final Random mockRandom = mock();
    private LocalMdibAccess mdibAccess;

    @BeforeEach
    void setUp() throws PreprocessingException {
        reset(mockRandom);

        mdibAccess = new MdibAccessBuilder()
                .addDevice(SensorType.ANNE_CHEST, "SEM-0001")
                .addMetricChannel(SensorType.ANNE_CHEST, MetricChannel.VITALS)
                .addMetric(SensorType.ANNE_CHEST, Metric.HR, BigDecimal.ZERO, Instant.now())
                .build();
    }

    @Test
    void testNextState() {
        var emulator =
                new NumericMetricEmulator(mockRandom, mdibAccess, SensorType.ANNE_CHEST, Metric.HR, 60, 70, 1, 100);

        when(mockRandom.nextInt(11)).thenReturn(0);
        emulator.writeNextMetric();
        assertHr(60);

        when(mockRandom.nextInt(11)).thenReturn(10);
        emulator.writeNextMetric();
        assertHr(70);

        when(mockRandom.nextInt(11)).thenReturn(5);
        emulator.writeNextMetric();
        assertHr(65);
    }

    private void assertHr(double expectedHr) {
        var metricHandle = MdibHandles.getMetricHandle(SensorType.ANNE_CHEST, Metric.HR);
        var state = (NumericMetricState) mdibAccess.getState(metricHandle).orElseThrow();
        assertEquals(BigDecimal.valueOf(expectedHr), state.getMetricValue().getValue());
    }
}
