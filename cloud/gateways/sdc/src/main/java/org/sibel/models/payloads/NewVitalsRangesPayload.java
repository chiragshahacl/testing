package org.sibel.models.payloads;

import com.google.common.base.MoreObjects;
import com.google.common.base.Objects;
import java.util.List;
import org.sibel.models.payloads.internal.VitalsRangePayload;

@SuppressWarnings("PMD.UnusedPrivateField")
public class NewVitalsRangesPayload implements PayloadInterface {
    private String primary_identifier;

    private List<VitalsRangePayload> ranges;

    public NewVitalsRangesPayload(String devicePrimaryIdentifier, List<VitalsRangePayload> ranges) {
        this.primary_identifier = devicePrimaryIdentifier;
        this.ranges = ranges;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        NewVitalsRangesPayload that = (NewVitalsRangesPayload) o;
        return Objects.equal(primary_identifier, that.primary_identifier) && Objects.equal(ranges, that.ranges);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(primary_identifier, ranges);
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("primary_identifier", primary_identifier)
                .add("ranges", ranges)
                .toString();
    }
}
