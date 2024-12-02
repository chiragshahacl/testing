package org.sibel.models.events;

import com.google.common.base.MoreObjects;
import com.google.common.base.Objects;
import java.time.Instant;
import java.util.List;
import org.sibel.models.Sensor;

public class SensorsUpdateEvent extends Event {
    private final List<Sensor> connectedSensors;

    public SensorsUpdateEvent(
            String id, Instant timestamp, String pmId, String patientId, List<Sensor> connectedSensors) {
        super(EventType.SENSORS_UPDATE, id, timestamp, pmId, patientId);
        this.connectedSensors = connectedSensors;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        if (!super.equals(o)) return false;
        SensorsUpdateEvent that = (SensorsUpdateEvent) o;
        return Objects.equal(connectedSensors, that.connectedSensors);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(super.hashCode(), connectedSensors);
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("type", type)
                .add("id", id)
                .add("timestamp", timestamp)
                .add("pmId", pmId)
                .add("patientId", patientId)
                .add("connectedSensors", connectedSensors)
                .toString();
    }
}
