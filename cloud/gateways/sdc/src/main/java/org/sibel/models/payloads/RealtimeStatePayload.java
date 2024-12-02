package org.sibel.models.payloads;

import com.google.common.base.MoreObjects;
import com.google.common.base.Objects;

@SuppressWarnings("PMD.UnusedPrivateField")
public class RealtimeStatePayload implements PayloadInterface {
    private String device_primary_identifier;
    private Boolean connection_status;

    public RealtimeStatePayload(String devicePrimaryIdentifier, Boolean connectionStatus) {
        this.device_primary_identifier = devicePrimaryIdentifier;
        this.connection_status = connectionStatus;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        RealtimeStatePayload that = (RealtimeStatePayload) o;
        return Objects.equal(device_primary_identifier, that.device_primary_identifier)
                && Objects.equal(connection_status, that.connection_status);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(device_primary_identifier, connection_status);
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("device_primary_identifier", device_primary_identifier)
                .add("connection_status", connection_status)
                .toString();
    }
}
