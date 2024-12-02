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

public class AnneChestEmulator extends DeviceEmulator {

    public enum EcgMode {
        DEMO("emulator_datasets/ecg_demo.csv"),
        SINUSOIDAL("emulator_datasets/ecg_sinusoidal.csv");

        public final String csvResource;

        EcgMode(String csvResource) {
            this.csvResource = csvResource;
        }
    }

    public AnneChestEmulator(LocalMdibAccess mdibAccess, EcgMode ecgMode) {
        super(
                SensorType.ANNE_CHEST.name(),
                List.of(
                        new WaveformMetricEmulator(
                                mdibAccess,
                                SensorType.ANNE_CHEST,
                                Metric.ECG_WAVEFORM,
                                EmulatorUtils.loadCsvDataSet(ecgMode.csvResource, "ecg"),
                                500),
                        new WaveformMetricEmulator(
                                mdibAccess,
                                SensorType.ANNE_CHEST,
                                Metric.RR_WAVEFORM,
                                EmulatorUtils.loadCsvDataSet("emulator_datasets/vitals_demo.csv", "RR(rpm)"),
                                500),
                        new NumericMetricEmulator(mdibAccess, SensorType.ANNE_CHEST, Metric.HR, 60, 70, 1),
                        new NumericMetricEmulator(
                                mdibAccess, SensorType.ANNE_CHEST, Metric.CHEST_TEMP, 96.8, 98.4, 0.2),
                        new NumericMetricEmulator(mdibAccess, SensorType.ANNE_CHEST, Metric.FALLS, 0, 0, 1),
                        new EnumStringMetricEmulator(
                                mdibAccess,
                                SensorType.ANNE_CHEST,
                                Metric.BODY_POSITION,
                                List.of("UPRIGHT", "SUPINE", "PRONE", "RIGHT", "LEFT")),
                        new NumericMetricEmulator(mdibAccess, SensorType.ANNE_CHEST, Metric.RR_METRIC, 12, 15, 1),
                        new NumericMetricEmulator(mdibAccess, SensorType.ANNE_CHEST, Metric.DEVICE_SIGNAL, -80, 0, 5),
                        new BatteryMetricEmulator(mdibAccess, SensorType.ANNE_CHEST, 0.6, 1.0, 0.05),
                        new EnumStringMetricEmulator(
                                mdibAccess, SensorType.ANNE_CHEST, Metric.DEVICE_LEAD, List.of("true")),
                        new EnumStringMetricEmulator(
                                mdibAccess, SensorType.ANNE_CHEST, Metric.DEVICE_MODULE, List.of("true"))));
    }
}
