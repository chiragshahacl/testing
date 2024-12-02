package org.sibel.emulator.metrics;

import static org.sibel.mdib.MdibStateFactory.createStringMetricState;

import java.time.Instant;
import java.util.List;
import java.util.Random;
import org.sibel.constants.EmulatorDefaults;
import org.sibel.constants.Metric;
import org.sibel.constants.SensorType;
import org.somda.sdc.biceps.common.MdibStateModifications;
import org.somda.sdc.biceps.model.participant.AbstractState;
import org.somda.sdc.biceps.provider.access.LocalMdibAccess;

public class EnumStringMetricEmulator extends AbstractMetricEmulator {
    private final Random random;
    private final List<String> values;

    public EnumStringMetricEmulator(
            LocalMdibAccess mdibAccess, SensorType sensorType, Metric metric, List<String> values) {
        this(new Random(), mdibAccess, sensorType, metric, values, (int)
                (1000 / EmulatorDefaults.ratePerSecond.get(metric)));
    }

    public EnumStringMetricEmulator(
            Random random,
            LocalMdibAccess mdibAccess,
            SensorType sensorType,
            Metric metric,
            List<String> values,
            int bufferingRateMillis) {
        super(mdibAccess, sensorType, metric, MdibStateModifications.Type.METRIC, bufferingRateMillis);
        this.random = random;
        this.values = values;
    }

    @Override
    public AbstractState getNextMetricState() {
        return createStringMetricState(sensorType, metric, getNextValue(), Instant.now());
    }

    private String getNextValue() {
        return values.get(random.nextInt(values.size()));
    }
}
