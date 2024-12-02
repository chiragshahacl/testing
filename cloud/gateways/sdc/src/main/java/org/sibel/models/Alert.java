package org.sibel.models;

import java.time.Instant;

public record Alert(
        AlertType type,
        String code,
        Sensor sensor,
        AlertPriority priority,
        boolean active,
        boolean latching,
        Instant determinationTime,
        VitalRange vitalRange) {}
