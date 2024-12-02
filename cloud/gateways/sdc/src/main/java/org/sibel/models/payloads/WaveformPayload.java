package org.sibel.models.payloads;

import com.google.common.base.MoreObjects;
import com.google.common.base.Objects;
import java.math.BigDecimal;
import java.time.Duration;
import java.time.Instant;
import java.util.List;

@SuppressWarnings("PMD.UnusedPrivateField")
public class WaveformPayload implements PayloadInterface {
    private String patient_id;
    private String patient_primary_identifier;
    private List<BigDecimal> samples;
    private Instant determination_time;
    private String sample_period;
    private String determination_period;
    private String code;
    private String device_code;
    private String device_primary_identifier;

    public WaveformPayload(
            String patientPrimaryIdentifier,
            List<BigDecimal> samples,
            Instant determinationTime,
            Duration samplePeriod,
            Duration determinationPeriod,
            String code,
            String deviceCode,
            String devicePrimaryIdentifier) {
        this.patient_id = patientPrimaryIdentifier;
        this.patient_primary_identifier = patientPrimaryIdentifier;
        this.samples = samples;
        this.determination_time = determinationTime;
        this.sample_period = samplePeriod.toString();
        determination_period = determinationPeriod.toString();
        this.code = code;
        this.device_code = deviceCode;
        this.device_primary_identifier = devicePrimaryIdentifier;
    }

    public String getPatientId() {
        return patient_id;
    }

    public String getPatientPrimaryIdentifier() {
        return patient_primary_identifier;
    }

    public List<BigDecimal> getSamples() {
        return samples;
    }

    public Instant getDeterminationTime() {
        return determination_time;
    }

    public String getSamplePeriod() {
        return sample_period;
    }

    public String getCode() {
        return code;
    }

    public String getDeviceCode() {
        return device_code;
    }

    public String getDevicePrimaryIdentifier() {
        return device_primary_identifier;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        WaveformPayload that = (WaveformPayload) o;
        return Objects.equal(patient_id, that.patient_id)
                && Objects.equal(patient_primary_identifier, that.patient_primary_identifier)
                && Objects.equal(samples, that.samples)
                && Objects.equal(determination_time, that.determination_time)
                && Objects.equal(sample_period, that.sample_period)
                && Objects.equal(determination_period, that.determination_period)
                && Objects.equal(code, that.code)
                && Objects.equal(device_code, that.device_code)
                && Objects.equal(device_primary_identifier, that.device_primary_identifier);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(
                patient_id,
                patient_primary_identifier,
                samples,
                determination_time,
                sample_period,
                determination_period,
                code,
                device_code,
                device_primary_identifier);
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("patient_id", patient_id)
                .add("patient_primary_identifier", patient_primary_identifier)
                .add("samples", samples)
                .add("determination_time", determination_time)
                .add("sample_period", sample_period)
                .add("determination_period", determination_period)
                .add("code", code)
                .add("device_code", device_code)
                .add("device_primary_identifier", device_primary_identifier)
                .toString();
    }
}
