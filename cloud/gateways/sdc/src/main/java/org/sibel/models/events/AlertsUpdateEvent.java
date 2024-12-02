package org.sibel.models.events;

import com.google.common.base.MoreObjects;
import com.google.common.base.Objects;
import java.time.Instant;
import java.util.List;
import org.sibel.models.Alert;

public class AlertsUpdateEvent extends Event {
    private final List<Alert> alerts;

    public AlertsUpdateEvent(String id, Instant timestamp, String pmId, String patientId, List<Alert> alerts) {
        super(EventType.ALERTS_UPDATE, id, timestamp, pmId, patientId);
        this.alerts = alerts;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        if (!super.equals(o)) return false;
        AlertsUpdateEvent that = (AlertsUpdateEvent) o;
        return Objects.equal(alerts, that.alerts);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(super.hashCode(), alerts);
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("type", type)
                .add("id", id)
                .add("timestamp", timestamp)
                .add("pmId", pmId)
                .add("patientId", patientId)
                .add("alerts", alerts)
                .toString();
    }
}
