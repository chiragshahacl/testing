package org.sibel.models;

import java.math.BigDecimal;

public record VitalRange(String code, BigDecimal lowerLimit, BigDecimal upperLimit) {}
