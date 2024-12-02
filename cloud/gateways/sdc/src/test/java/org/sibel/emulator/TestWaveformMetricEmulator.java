package org.sibel.emulator;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.google.common.collect.Streams;
import java.math.BigDecimal;
import java.time.Duration;
import java.time.Instant;
import java.util.Collections;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.sibel.constants.MdibHandles;
import org.sibel.constants.Metric;
import org.sibel.constants.MetricChannel;
import org.sibel.constants.SensorType;
import org.sibel.emulator.metrics.WaveformMetricEmulator;
import org.sibel.mdib.MdibAccessBuilder;
import org.somda.sdc.biceps.common.storage.PreprocessingException;
import org.somda.sdc.biceps.model.participant.RealTimeSampleArrayMetricState;
import org.somda.sdc.biceps.provider.access.LocalMdibAccess;

class TestWaveformMetricEmulator {
    private LocalMdibAccess mdibAccess;

    @BeforeEach
    void setUp() throws PreprocessingException {
        mdibAccess = new MdibAccessBuilder()
                .addDevice(SensorType.ANNE_CHEST, "SEM-0001")
                .addMetricChannel(SensorType.ANNE_CHEST, MetricChannel.VITALS)
                .addRealTimeMetric(
                        SensorType.ANNE_CHEST,
                        Metric.ECG_WAVEFORM,
                        List.of(BigDecimal.ZERO, BigDecimal.ZERO, BigDecimal.ZERO),
                        Duration.ofMillis(100),
                        Duration.ofMillis(100),
                        Instant.now())
                .build();
    }

    @Test
    void testNextState() {
        var expectedSamplesPerMessage = Math.round(256f / 1000 * 80);
        var dataSet = Streams.concat(
                        Streams.concat(
                                Collections.nCopies(expectedSamplesPerMessage, BigDecimal.ONE).stream(),
                                Collections.nCopies(expectedSamplesPerMessage, BigDecimal.TWO).stream()),
                        Collections.nCopies(expectedSamplesPerMessage / 2, BigDecimal.TEN).stream())
                .toList();
        var emulator =
                new WaveformMetricEmulator(mdibAccess, SensorType.ANNE_CHEST, Metric.ECG_WAVEFORM, dataSet, 256f, 80);

        emulator.writeNextMetric();
        assertEcgSample(Collections.nCopies(expectedSamplesPerMessage, BigDecimal.ONE));

        emulator.writeNextMetric();
        assertEcgSample(Collections.nCopies(expectedSamplesPerMessage, BigDecimal.TWO));

        emulator.writeNextMetric();
        assertEcgSample(Streams.concat(
                        Collections.nCopies(expectedSamplesPerMessage / 2, BigDecimal.TEN).stream(),
                        Collections.nCopies(expectedSamplesPerMessage / 2, BigDecimal.ONE).stream())
                .toList());
    }

    private void assertEcgSample(List<BigDecimal> expectedSample) {
        var metricHandle = MdibHandles.getMetricHandle(SensorType.ANNE_CHEST, Metric.ECG_WAVEFORM);
        var state = (RealTimeSampleArrayMetricState)
                mdibAccess.getState(metricHandle).orElseThrow();
        assertEquals(expectedSample, state.getMetricValue().getSamples());
    }
}
