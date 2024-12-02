package org.sibel.models.events;

import com.google.common.base.MoreObjects;
import com.google.common.base.Objects;
import java.time.Instant;
import java.util.List;
import org.sibel.models.VitalRange;

public class VitalRangesUpdateEvent extends Event {
    private final List<VitalRange> vitalRanges;

    public VitalRangesUpdateEvent(
            String id, Instant timestamp, String pmId, String patientId, List<VitalRange> vitalRanges) {
        super(EventType.VITAL_RANGES_UPDATE, id, timestamp, pmId, patientId);
        this.vitalRanges = vitalRanges;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        if (!super.equals(o)) return false;
        VitalRangesUpdateEvent that = (VitalRangesUpdateEvent) o;
        return Objects.equal(vitalRanges, that.vitalRanges);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(super.hashCode(), vitalRanges);
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("type", type)
                .add("id", id)
                .add("timestamp", timestamp)
                .add("pmId", pmId)
                .add("patientId", patientId)
                .add("vitalRanges", vitalRanges)
                .toString();
    }
}
