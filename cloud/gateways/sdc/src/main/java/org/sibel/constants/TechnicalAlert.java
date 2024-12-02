package org.sibel.constants;

import java.math.BigDecimal;
import org.somda.sdc.biceps.model.participant.AlertConditionPriority;

public enum TechnicalAlert {
    LEAD_OFF("258110", AlertConditionPriority.LO, Metric.DEVICE_LEAD, Condition.LEAD_OFF_CONDITION, "leadoff");

    public final String code;
    public final AlertConditionPriority priority;
    public final Metric metric;
    public final Condition condition;
    public final String handle;

    TechnicalAlert(String code, AlertConditionPriority priority, Metric metric, Condition condition, String handle) {
        this.code = code;
        this.priority = priority;
        this.condition = condition;
        this.handle = handle;
        this.metric = metric;
    }

    public enum Condition {
        LEAD_OFF_CONDITION("145206", null, null);

        public final String code;
        public final BigDecimal upperLimit;
        public final BigDecimal lowerLimit;

        Condition(String code, BigDecimal upperLimit, BigDecimal lowerLimit) {
            this.code = code;
            this.upperLimit = upperLimit;
            this.lowerLimit = lowerLimit;
        }
    }
}
