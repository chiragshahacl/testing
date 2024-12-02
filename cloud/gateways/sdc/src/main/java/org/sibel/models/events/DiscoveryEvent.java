package org.sibel.models.events;

import com.google.common.base.MoreObjects;
import com.google.common.base.Objects;
import java.time.Instant;
import java.util.List;
import org.sibel.models.Alert;
import org.sibel.models.Patient;
import org.sibel.models.Sensor;
import org.sibel.models.VitalRange;

public class DiscoveryEvent extends Event {
    private final Patient patient;
    private final List<Sensor> connectedSensors;
    private final List<VitalRange> vitalRanges;
    private final List<Alert> alerts;

    public DiscoveryEvent(
            String id,
            Instant timestamp,
            String pmId,
            String patientId,
            Patient patient,
            List<Sensor> connectedSensors,
            List<VitalRange> vitalRanges,
            List<Alert> alerts) {
        super(EventType.DISCOVERY, id, timestamp, pmId, patientId);
        this.patient = patient;
        this.connectedSensors = connectedSensors;
        this.vitalRanges = vitalRanges;
        this.alerts = alerts;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        if (!super.equals(o)) return false;
        DiscoveryEvent that = (DiscoveryEvent) o;
        return Objects.equal(patient, that.patient)
                && Objects.equal(connectedSensors, that.connectedSensors)
                && Objects.equal(vitalRanges, that.vitalRanges)
                && Objects.equal(alerts, that.alerts);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(super.hashCode(), patient, connectedSensors, vitalRanges, alerts);
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
                .add("connectedSensors", connectedSensors)
                .add("vitalRanges", vitalRanges)
                .add("alerts", alerts)
                .toString();
    }
}
