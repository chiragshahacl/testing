package org.sibel.models.payloads;

import com.google.common.base.MoreObjects;
import com.google.common.base.Objects;
import java.time.Instant;
import org.sibel.models.payloads.internal.VitalsRangePayload;

@SuppressWarnings("PMD.UnusedPrivateField")
public class AlertPayload implements PayloadInterface {
    private final String patient_primary_identifier;
    private final String patient_id;
    private final Boolean active;
    private final Boolean latching;
    private final String code;
    private final String device_code;
    private final String priority;
    private final Instant determination_time;
    private final String device_primary_identifier;
    private final VitalsRangePayload vital_range;

    public AlertPayload(
            String patientPrimaryIdentifier,
            Boolean active,
            Boolean latching,
            String alertCode,
            String deviceCode,
            String priority,
            Instant determinationTime,
            String devicePrimaryIdentifier,
            VitalsRangePayload vitalsRange) {
        // TODO: deprecate in favor of patient_primary_identifier
        this.patient_id = patientPrimaryIdentifier;
        this.patient_primary_identifier = patientPrimaryIdentifier;
        this.active = active;
        this.latching = latching;
        this.code = alertCode;
        this.device_code = deviceCode;
        this.priority = priority;
        this.determination_time = determinationTime;
        this.device_primary_identifier = devicePrimaryIdentifier;
        this.vital_range = vitalsRange;
    }

    public String getCode() {
        return code;
    }

    public String getDeviceCode() {
        return device_code;
    }

    public Boolean getActive() {
        return active;
    }

    public Boolean getlatching() {
        return latching;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        AlertPayload that = (AlertPayload) o;
        return Objects.equal(patient_primary_identifier, that.patient_primary_identifier)
                && Objects.equal(patient_id, that.patient_id)
                && Objects.equal(active, that.active)
                && Objects.equal(latching, that.latching)
                && Objects.equal(code, that.code)
                && Objects.equal(device_code, that.device_code)
                && Objects.equal(priority, that.priority)
                && Objects.equal(determination_time, that.determination_time)
                && Objects.equal(device_primary_identifier, that.device_primary_identifier)
                && Objects.equal(vital_range, that.vital_range);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(
                patient_primary_identifier,
                patient_id,
                active,
                latching,
                code,
                device_code,
                priority,
                determination_time,
                device_primary_identifier,
                vital_range);
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("patient_primary_identifier", patient_primary_identifier)
                .add("patient_id", patient_id)
                .add("active", active)
                .add("latching", latching)
                .add("code", code)
                .add("device_code", device_code)
                .add("priority", priority)
                .add("determination_time", determination_time)
                .add("device_primary_identifier", device_primary_identifier)
                .add("range", vital_range)
                .toString();
    }
}
