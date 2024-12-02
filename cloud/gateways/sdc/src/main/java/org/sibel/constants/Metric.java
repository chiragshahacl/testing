package org.sibel.constants;

import java.util.List;

public enum Metric {
    HR("147844", UnitCodes.BEATS_PER_MINUTE, MetricChannel.VITALS, "hr"),
    BODY_POSITION(
            "192513",
            UnitCodes.NO_UNIT,
            MetricChannel.VITALS,
            List.of(
                    new Value("145228", "UPRIGHT"),
                    new Value("145229", "SUPINE"),
                    new Value("145230", "PRONE"),
                    new Value("145231", "RIGHT"),
                    new Value("145232", "LEFT")),
            "bodyposition"),
    BODY_ANGLE_UPRIGHT("192530", UnitCodes.ANGLE_DEGREE, MetricChannel.VITALS, "bodyangle.upright"),
    BATTERY("65577", UnitCodes.PERCENTAGE, MetricChannel.VITALS),
    ECG_WAVEFORM("131328", UnitCodes.MILLIVOLT, MetricChannel.VITALS, "ecgwaveform"),
    CHEST_TEMP("150388", UnitCodes.FAHRENHEIT, MetricChannel.VITALS, "temp"),
    LIMB_TEMP("150388", UnitCodes.FAHRENHEIT, MetricChannel.VITALS, "temp"),
    FALLS("192512", UnitCodes.NO_UNIT, MetricChannel.VITALS, "fall"),
    RR_WAVEFORM("151780", UnitCodes.BREATH_PER_MINUTE, MetricChannel.VITALS, "rrwaveform"),
    RR_METRIC("151556", UnitCodes.BREATH_PER_MINUTE, MetricChannel.VITALS, "rr"),
    PLETH_WAVEFORM("150452", UnitCodes.NO_UNIT, MetricChannel.VITALS, "ppgwaveform"),
    SPO2("150316", UnitCodes.PERCENTAGE, MetricChannel.VITALS, "spo2"),
    PR("149540", UnitCodes.BEATS_PER_MINUTE, MetricChannel.VITALS, "pr"),
    PI("150488", UnitCodes.PERCENTAGE, MetricChannel.VITALS, "pi"),
    DEVICE_SIGNAL("192522", UnitCodes.NO_UNIT, MetricChannel.DEVICE, "rssi"),
    DEVICE_LEAD(
            "145221",
            UnitCodes.NO_UNIT,
            MetricChannel.DEVICE,
            List.of(new Value("145997", "true"), new Value("145998", "false")),
            "lead"),
    DEVICE_MODULE(
            "145224",
            UnitCodes.NO_UNIT,
            MetricChannel.DEVICE,
            List.of(new Value("145997", "true"), new Value("145998", "false")),
            "module");

    public final String code;
    public final String unitCode;
    public final MetricChannel channel;
    public final String handle;
    public final List<Value> allowedValues;

    public record Value(String code, String value) {}

    Metric(String code, String unitCode, MetricChannel channel, List<Value> allowedValues, String handle) {
        this.code = code;
        this.unitCode = unitCode;
        this.channel = channel;
        this.handle = handle;
        this.allowedValues = allowedValues;
    }

    Metric(String code, String unitCode, MetricChannel channel, String handle) {
        this(code, unitCode, channel, List.of(), handle);
    }

    Metric(String code, String unitCode, MetricChannel channel) {
        this(code, unitCode, channel, List.of(), null);
    }
}
