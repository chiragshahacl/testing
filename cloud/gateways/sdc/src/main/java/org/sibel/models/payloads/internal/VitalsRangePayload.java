package org.sibel.models.payloads.internal;

import com.google.common.base.MoreObjects;
import java.math.BigDecimal;
import java.util.Objects;

public class VitalsRangePayload {
    private String code;
    private BigDecimal upper_limit;
    private BigDecimal lower_limit;
    private boolean alert_condition_enabled;

    public VitalsRangePayload(
            String code, BigDecimal upperLimit, BigDecimal lowerLimit, boolean alertConditionEnabled) {
        this.code = code;
        this.upper_limit = upperLimit;
        this.lower_limit = lowerLimit;
        alert_condition_enabled = alertConditionEnabled;
    }

    public String getCode() {
        return code;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof VitalsRangePayload)) return false;
        VitalsRangePayload that = (VitalsRangePayload) o;
        return Objects.equals(code, that.code)
                && Objects.equals(upper_limit, that.upper_limit)
                && Objects.equals(lower_limit, that.lower_limit)
                && Objects.equals(alert_condition_enabled, that.alert_condition_enabled);
    }

    @Override
    public int hashCode() {
        return Objects.hash(code, upper_limit, lower_limit, alert_condition_enabled);
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("code", code)
                .add("upper_limit", upper_limit)
                .add("lower_limit", lower_limit)
                .add("alert_condition_enabled", alert_condition_enabled)
                .toString();
    }
}
