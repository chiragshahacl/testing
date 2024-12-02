package org.sibel.models.events;

import com.google.common.base.MoreObjects;
import com.google.common.base.Objects;
import java.time.Instant;
import java.util.List;
import org.sibel.models.WaveformUpdate;

public class WaveformsUpdateEvent extends Event {
    private final List<WaveformUpdate> waveformUpdates;

    public WaveformsUpdateEvent(
            String id, Instant timestamp, String pmId, String patientId, List<WaveformUpdate> waveformUpdates) {
        super(EventType.WAVEFORMS_UPDATE, id, timestamp, pmId, patientId);
        this.waveformUpdates = waveformUpdates;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        if (!super.equals(o)) return false;
        WaveformsUpdateEvent that = (WaveformsUpdateEvent) o;
        return Objects.equal(waveformUpdates, that.waveformUpdates);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(super.hashCode(), waveformUpdates);
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("type", type)
                .add("id", id)
                .add("timestamp", timestamp)
                .add("pmId", pmId)
                .add("patientId", patientId)
                .add("waveformUpdates", waveformUpdates)
                .toString();
    }
}
