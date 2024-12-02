package org.sibel.models.events;

import com.google.common.base.MoreObjects;
import com.google.common.base.Objects;
import java.time.Instant;
import org.sibel.models.Patient;

public abstract class PatientUpdateEvent extends Event {
    protected final Patient patient;

    public PatientUpdateEvent(
            EventType type, String id, Instant timestamp, String pmId, String patientId, Patient patient) {
        super(type, id, timestamp, pmId, patientId);
        this.patient = patient;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        if (!super.equals(o)) return false;
        PatientUpdateEvent that = (PatientUpdateEvent) o;
        return Objects.equal(patient, that.patient);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(super.hashCode(), patient);
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("type", type)
                .add("id", id)
                .add("timestamp", timestamp)
                .add("pmId", pmId)
                .add("patientId", patientId)
                .add("patient", patient)
                .toString();
    }
}
