package org.sibel.models.events;

import com.google.common.base.MoreObjects;
import com.google.common.base.Objects;
import com.google.gson.annotations.SerializedName;
import java.time.Instant;

public abstract class Event {
    @SerializedName("event_type")
    protected final EventType type;

    protected final String id;
    protected final Instant timestamp;
    protected final String pmId;
    protected final String patientId;

    public Event(EventType type, String id, Instant timestamp, String pmId, String patientId) {
        this.type = type;
        this.id = id;
        this.timestamp = timestamp;
        this.pmId = pmId;
        this.patientId = patientId;
    }

    public String getId() {
        return id;
    }

    public EventType getType() {
        return type;
    }

    public Instant getTimestamp() {
        return timestamp;
    }

    public String getPmId() {
        return pmId;
    }

    public String getPatientId() {
        return patientId;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Event event = (Event) o;
        return Objects.equal(id, event.id)
                && type == event.type
                && Objects.equal(timestamp, event.timestamp)
                && Objects.equal(pmId, event.pmId)
                && Objects.equal(patientId, event.patientId);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(id, type, timestamp, pmId, patientId);
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("type", type)
                .add("id", id)
                .add("timestamp", timestamp)
                .add("pmId", pmId)
                .add("patientId", patientId)
                .toString();
    }
}
