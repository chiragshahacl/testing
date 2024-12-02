package org.sibel.constants;

public enum MetricChannel {
    VITALS("metric"),
    DEVICE("device");

    public final String name;

    MetricChannel(String name) {
        this.name = name;
    }
}
