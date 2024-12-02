package org.sibel.models.payloads;

import com.google.common.base.MoreObjects;
import com.google.common.base.Objects;
import org.sibel.models.payloads.internal.DevicePayload;
import org.sibel.models.payloads.internal.PatientPayload;

@SuppressWarnings("PMD.UnusedPrivateField")
public class DeviceDiscoveredPayload implements PayloadInterface {
    private DevicePayload device;
    private PatientPayload patient;

    public DeviceDiscoveredPayload(DevicePayload device, PatientPayload patient) {
        this.device = device;
        this.patient = patient;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        DeviceDiscoveredPayload that = (DeviceDiscoveredPayload) o;
        return Objects.equal(device, that.device) && Objects.equal(patient, that.patient);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(device, patient);
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("device", device)
                .add("patient", patient)
                .toString();
    }
}
