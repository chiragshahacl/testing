package org.sibel.models;

import java.time.Instant;

public record MetricUpdate<T>(String code, Sensor sensor, T value, String unitCode, Instant determinationTime) {}
