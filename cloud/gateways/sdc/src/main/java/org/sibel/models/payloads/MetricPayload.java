package org.sibel.models.payloads;

import com.google.common.base.MoreObjects;
import com.google.common.base.Objects;
import java.time.Instant;
import java.util.List;

@SuppressWarnings("PMD.UnusedPrivateField")
public class MetricPayload<T> implements PayloadInterface {
    private String patient_id;
    private String patient_primary_identifier;
    private List<T> samples;
    private Instant determination_time;
    private String code;
    private String device_code;
    private String unit_code;
    private String device_primary_identifier;

    public MetricPayload(
            String patientPrimaryIdentifier,
            List<T> samples,
            Instant determinationTime,
            String code,
            String deviceCode,
            String devicePrimaryIdentifier) {
        this(patientPrimaryIdentifier, samples, determinationTime, code, null, deviceCode, devicePrimaryIdentifier);
    }

    public MetricPayload(
            String patientPrimaryIdentifier,
            List<T> samples,
            Instant determinationTime,
            String code,
            String unitCode,
            String deviceCode,
            String devicePrimaryIdentifier) {
        this.patient_id = patientPrimaryIdentifier;
        this.patient_primary_identifier = patientPrimaryIdentifier;
        this.samples = samples;
        this.determination_time = determinationTime;
        this.code = code;
        this.unit_code = unitCode;
        this.device_code = deviceCode;
        this.device_primary_identifier = devicePrimaryIdentifier;
    }

    public String getPatientId() {
        return patient_id;
    }

    public String getPatientPrimaryIdentifier() {
        return patient_primary_identifier;
    }

    public List<T> getSamples() {
        return samples;
    }

    public Instant getDeterminationTime() {
        return determination_time;
    }

    public String getCode() {
        return code;
    }

    public String getDeviceCode() {
        return device_code;
    }

    public String getUnitCode() {
        return unit_code;
    }

    public String getDevicePrimaryIdentifier() {
        return device_primary_identifier;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        MetricPayload<?> that = (MetricPayload<?>) o;
        return Objects.equal(patient_id, that.patient_id)
                && Objects.equal(patient_primary_identifier, that.patient_primary_identifier)
                && Objects.equal(samples, that.samples)
                && Objects.equal(determination_time, that.determination_time)
                && Objects.equal(code, that.code)
                && Objects.equal(device_code, that.device_code)
                && Objects.equal(unit_code, that.unit_code)
                && Objects.equal(device_primary_identifier, that.device_primary_identifier);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(
                patient_id,
                patient_primary_identifier,
                samples,
                determination_time,
                code,
                device_code,
                unit_code,
                device_primary_identifier);
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("patient_id", patient_id)
                .add("patient_primary_identifier", patient_primary_identifier)
                .add("samples", samples)
                .add("determination_time", determination_time)
                .add("code", code)
                .add("device_code", device_code)
                .add("unit_code", unit_code)
                .add("device_primary_identifier", device_primary_identifier)
                .toString();
    }
}
