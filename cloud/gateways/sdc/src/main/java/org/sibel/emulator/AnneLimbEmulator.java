package org.sibel.emulator;

import java.util.List;
import org.sibel.constants.Metric;
import org.sibel.constants.SensorType;
import org.sibel.emulator.metrics.BatteryMetricEmulator;
import org.sibel.emulator.metrics.EnumStringMetricEmulator;
import org.sibel.emulator.metrics.NumericMetricEmulator;
import org.sibel.emulator.metrics.WaveformMetricEmulator;
import org.sibel.utils.EmulatorUtils;
import org.somda.sdc.biceps.provider.access.LocalMdibAccess;

public class AnneLimbEmulator extends DeviceEmulator {

    public AnneLimbEmulator(LocalMdibAccess mdibAccess) {
        super(
                SensorType.ANNE_LIMB.name(),
                List.of(
                        new WaveformMetricEmulator(
                                mdibAccess,
                                SensorType.ANNE_LIMB,
                                Metric.PLETH_WAVEFORM,
                                EmulatorUtils.loadCsvDataSet("emulator_datasets/vitals_demo.csv", "RR(rpm)"),
                                500),
                        new NumericMetricEmulator(mdibAccess, SensorType.ANNE_LIMB, Metric.SPO2, 95, 99, 1),
                        new NumericMetricEmulator(mdibAccess, SensorType.ANNE_LIMB, Metric.PR, 80, 110, 2),
                        new NumericMetricEmulator(mdibAccess, SensorType.ANNE_LIMB, Metric.PI, 4, 5, 0.1),
                        new NumericMetricEmulator(mdibAccess, SensorType.ANNE_LIMB, Metric.LIMB_TEMP, 96.8, 98.4, 0.2),
                        new NumericMetricEmulator(mdibAccess, SensorType.ANNE_LIMB, Metric.DEVICE_SIGNAL, -80, 0, 5),
                        new BatteryMetricEmulator(mdibAccess, SensorType.ANNE_LIMB, 0.6, 1.0, 0.05),
                        new EnumStringMetricEmulator(
                                mdibAccess, SensorType.ANNE_LIMB, Metric.DEVICE_LEAD, List.of("true")),
                        new EnumStringMetricEmulator(
                                mdibAccess, SensorType.ANNE_LIMB, Metric.DEVICE_MODULE, List.of("true"))));
    }
}
