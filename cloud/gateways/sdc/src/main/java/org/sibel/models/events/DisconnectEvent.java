package org.sibel.models.events;

import java.time.Instant;

public class DisconnectEvent extends Event {
    public DisconnectEvent(String id, Instant timestamp, String pmId, String patientId) {
        super(EventType.DISCONNECT, id, timestamp, pmId, patientId);
    }
}
