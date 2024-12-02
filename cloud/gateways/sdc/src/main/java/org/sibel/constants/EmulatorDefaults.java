package org.sibel.constants;

import java.util.Map;

public final class EmulatorDefaults {
    public static Map<Metric, Float> ratePerSecond = Map.ofEntries(
            Map.entry(Metric.HR, 1f),
            Map.entry(Metric.BODY_POSITION, 2f / 60f),
            Map.entry(Metric.BATTERY, 1f / 60f),
            Map.entry(Metric.ECG_WAVEFORM, 256f),
            Map.entry(Metric.CHEST_TEMP, 1.0f),
            Map.entry(Metric.FALLS, 2f / 60f),
            Map.entry(Metric.RR_WAVEFORM, 26f),
            Map.entry(Metric.RR_METRIC, 10f),
            Map.entry(Metric.PLETH_WAVEFORM, 128f),
            Map.entry(Metric.SPO2, 1.0f),
            Map.entry(Metric.LIMB_TEMP, 1.0f),
            Map.entry(Metric.PI, 1.0f),
            Map.entry(Metric.PR, 1.0f),
            Map.entry(Metric.DEVICE_SIGNAL, 1f / 60f),
            Map.entry(Metric.DEVICE_LEAD, 1f / 60f),
            Map.entry(Metric.DEVICE_MODULE, 1f / 60f));
}
