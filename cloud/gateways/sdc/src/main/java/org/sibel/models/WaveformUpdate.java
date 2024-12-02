package org.sibel.models;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;

public record WaveformUpdate(
        String code,
        Sensor sensor,
        List<BigDecimal> samples,
        String unitCode,
        Instant determinationTime,
        String determinationPeriod,
        String samplePeriod) {}
