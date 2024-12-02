package org.sibel.models.payloads;

import com.google.common.base.MoreObjects;
import com.google.common.base.Objects;
import java.time.Instant;

@SuppressWarnings("PMD.UnusedPrivateField")
public class SensorRemovedPayload implements PayloadInterface {
    private final String device_primary_identifier;
    private final String patient_primary_identifier;
    private final String determination_time;

    public SensorRemovedPayload(
            String devicePrimaryIdentifier, String patientPrimaryIdentifier, Instant determinationTime) {
        device_primary_identifier = devicePrimaryIdentifier;
        patient_primary_identifier = patientPrimaryIdentifier;
        determination_time = Long.toString(determinationTime.toEpochMilli());
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        SensorRemovedPayload that = (SensorRemovedPayload) o;
        return Objects.equal(device_primary_identifier, that.device_primary_identifier)
                && Objects.equal(patient_primary_identifier, that.patient_primary_identifier)
                && Objects.equal(determination_time, that.determination_time);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(device_primary_identifier, determination_time, patient_primary_identifier);
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("device_primary_identifier", device_primary_identifier)
                .add("patient_primary_identifier", patient_primary_identifier)
                .add("determination_time", determination_time)
                .toString();
    }
}
