package org.sibel.emulator.metrics;

import static org.sibel.mdib.MdibStateFactory.createNumericMetricState;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.Random;
import org.sibel.constants.EmulatorDefaults;
import org.sibel.constants.Metric;
import org.sibel.constants.SensorType;
import org.somda.sdc.biceps.common.MdibStateModifications;
import org.somda.sdc.biceps.model.participant.AbstractState;
import org.somda.sdc.biceps.provider.access.LocalMdibAccess;

public class NumericMetricEmulator extends AbstractMetricEmulator {
    private final Random random;
    private final double minValue;
    private final double maxValue;
    private final double step;

    public NumericMetricEmulator(
            LocalMdibAccess mdibAccess,
            SensorType sensorType,
            Metric metric,
            double minValue,
            double maxValue,
            double step) {
        this(new Random(), mdibAccess, sensorType, metric, minValue, maxValue, step, (int)
                (1000 / EmulatorDefaults.ratePerSecond.get(metric)));
    }

    public NumericMetricEmulator(
            Random random,
            LocalMdibAccess mdibAccess,
            SensorType sensorType,
            Metric metric,
            double minValue,
            double maxValue,
            double step,
            int bufferingRateMillis) {
        super(mdibAccess, sensorType, metric, MdibStateModifications.Type.METRIC, bufferingRateMillis);
        this.random = random;
        this.minValue = minValue;
        this.maxValue = maxValue;
        this.step = step;
    }

    @Override
    public AbstractState getNextMetricState() {
        return createNumericMetricState(sensorType, metric, getNextValue(), Instant.now());
    }

    protected BigDecimal getNextValue() {
        var partitions = (int) Math.floor((maxValue - minValue) / step);
        var value = minValue + random.nextInt(partitions + 1) * step;
        return BigDecimal.valueOf(value);
    }
}
