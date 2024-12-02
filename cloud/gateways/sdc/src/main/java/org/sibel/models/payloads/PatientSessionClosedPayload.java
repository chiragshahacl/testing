package org.sibel.models.payloads;

import com.google.common.base.MoreObjects;
import com.google.common.base.Objects;

public class PatientSessionClosedPayload implements PayloadInterface {
    String patient_primary_identifier;
    String device_primary_identifier;

    public PatientSessionClosedPayload(String patient_primary_identifier, String device_primary_identifier) {
        this.patient_primary_identifier = patient_primary_identifier;
        this.device_primary_identifier = device_primary_identifier;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        PatientSessionClosedPayload that = (PatientSessionClosedPayload) o;
        return Objects.equal(patient_primary_identifier, that.patient_primary_identifier)
                && Objects.equal(device_primary_identifier, that.device_primary_identifier);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(patient_primary_identifier, device_primary_identifier);
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("patient_primary_identifier", patient_primary_identifier)
                .add("device_primary_identifier", device_primary_identifier)
                .toString();
    }
}
