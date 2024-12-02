package org.sibel.emulator.metrics;

import static org.sibel.mdib.MdibStateFactory.*;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;
import java.util.stream.Stream;
import org.sibel.constants.EmulatorDefaults;
import org.sibel.constants.Metric;
import org.sibel.constants.SensorType;
import org.somda.sdc.biceps.common.MdibStateModifications;
import org.somda.sdc.biceps.model.participant.AbstractState;
import org.somda.sdc.biceps.provider.access.LocalMdibAccess;

public class WaveformMetricEmulator extends AbstractMetricEmulator {
    private int currentSamplingIndex = 0;
    private final List<BigDecimal> dataSet;
    private final float ratePerSecond;

    public WaveformMetricEmulator(
            LocalMdibAccess mdibAccess,
            SensorType sensorType,
            Metric metric,
            List<BigDecimal> dataSet,
            int bufferingRateMillis) {
        this(mdibAccess, sensorType, metric, dataSet, EmulatorDefaults.ratePerSecond.get(metric), bufferingRateMillis);
    }

    public WaveformMetricEmulator(
            LocalMdibAccess mdibAccess,
            SensorType sensorType,
            Metric metric,
            List<BigDecimal> dataSet,
            float ratePerSecond,
            int bufferingRateMillis) {
        super(mdibAccess, sensorType, metric, MdibStateModifications.Type.WAVEFORM, bufferingRateMillis);
        this.dataSet = dataSet;
        this.ratePerSecond = ratePerSecond;
    }

    @Override
    public AbstractState getNextMetricState() {
        return createRealTimeMetricState(sensorType, metric, getNextSample(), Instant.now());
    }

    private List<BigDecimal> getNextSample() {
        var sampleSize = Math.round(ratePerSecond / 1000 * bufferingRateMillis);
        var nextSamplingIndex = (currentSamplingIndex + sampleSize) % dataSet.size();
        List<BigDecimal> sample;
        if (currentSamplingIndex < nextSamplingIndex) {
            sample = dataSet.subList(currentSamplingIndex, nextSamplingIndex);
        } else {
            sample = Stream.concat(
                            dataSet.subList(currentSamplingIndex, dataSet.size()).stream(),
                            dataSet.subList(0, nextSamplingIndex).stream())
                    .toList();
        }
        currentSamplingIndex = nextSamplingIndex;
        return sample;
    }
}
