package org.sibel.emulator.metrics;

import static org.sibel.mdib.MdibStateFactory.createBatteryState;

import java.util.Random;
import org.sibel.constants.EmulatorDefaults;
import org.sibel.constants.Metric;
import org.sibel.constants.SensorType;
import org.somda.sdc.biceps.model.participant.AbstractState;
import org.somda.sdc.biceps.model.participant.BatteryState;
import org.somda.sdc.biceps.provider.access.LocalMdibAccess;

public class BatteryMetricEmulator extends NumericMetricEmulator {
    public BatteryMetricEmulator(
            LocalMdibAccess mdibAccess, SensorType sensorType, double minValue, double maxValue, double step) {
        this(new Random(), mdibAccess, sensorType, minValue, maxValue, step, (int)
                (1000 / EmulatorDefaults.ratePerSecond.get(Metric.BATTERY)));
    }

    public BatteryMetricEmulator(
            Random random,
            LocalMdibAccess mdibAccess,
            SensorType sensorType,
            double minValue,
            double maxValue,
            double step,
            int bufferingRateMillis) {
        super(random, mdibAccess, sensorType, Metric.BATTERY, minValue, maxValue, step, bufferingRateMillis);
    }

    @Override
    public AbstractState getNextMetricState() {
        return createBatteryState(sensorType, getNextValue(), BatteryState.ChargeStatus.DIS_CH_B);
    }
}
