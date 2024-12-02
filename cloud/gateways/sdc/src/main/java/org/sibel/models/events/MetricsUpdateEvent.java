package org.sibel.models.events;

import com.google.common.base.MoreObjects;
import com.google.common.base.Objects;
import java.time.Instant;
import java.util.List;
import org.sibel.models.MetricUpdate;

public class MetricsUpdateEvent<T> extends Event {
    private final List<MetricUpdate<T>> metricUpdates;

    public MetricsUpdateEvent(
            String id, Instant timestamp, String pmId, String patientId, List<MetricUpdate<T>> metricUpdates) {
        super(EventType.METRICS_UPDATE, id, timestamp, pmId, patientId);
        this.metricUpdates = metricUpdates.stream().toList();
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        if (!super.equals(o)) return false;
        MetricsUpdateEvent<?> that = (MetricsUpdateEvent<?>) o;
        return Objects.equal(metricUpdates, that.metricUpdates);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(super.hashCode(), metricUpdates);
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("id", id)
                .add("timestamp", timestamp)
                .add("pmId", pmId)
                .add("patientId", patientId)
                .add("metricUpdates", metricUpdates)
                .toString();
    }
}
