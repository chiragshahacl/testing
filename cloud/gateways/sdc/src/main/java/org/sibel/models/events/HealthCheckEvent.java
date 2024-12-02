package org.sibel.models.events;

import java.time.Instant;

public class HealthCheckEvent extends Event {
    public HealthCheckEvent(String id, Instant timestamp, String pmId, String patientId) {
        super(EventType.HEALTH_CHECK, id, timestamp, pmId, patientId);
    }
}
