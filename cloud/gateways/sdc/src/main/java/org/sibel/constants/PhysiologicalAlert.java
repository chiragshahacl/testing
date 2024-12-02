package org.sibel.constants;

import java.math.BigDecimal;
import java.util.List;
import org.somda.sdc.biceps.model.participant.AlertConditionPriority;
import org.somda.sdc.biceps.model.participant.AlertSignalManifestation;

public enum PhysiologicalAlert {
    HR_ME__AUD("258049", AlertConditionPriority.ME, Condition.HR_THRESHOLD, AlertSignalManifestation.AUD),
    HR_ME__VIS("258050", AlertConditionPriority.ME, Condition.HR_THRESHOLD, AlertSignalManifestation.VIS),
    RR_ME__AUD("258061", AlertConditionPriority.ME, Condition.RR_THRESHOLD, AlertSignalManifestation.AUD),
    RR_ME__VIS("258062", AlertConditionPriority.ME, Condition.RR_THRESHOLD, AlertSignalManifestation.VIS);

    public final String code;
    public final AlertConditionPriority priority;
    public final Condition condition;
    public final AlertSignalManifestation manifestation;

    PhysiologicalAlert(
            String code, AlertConditionPriority priority, Condition condition, AlertSignalManifestation manifestation) {
        this.code = code;
        this.priority = priority;
        this.condition = condition;
        this.manifestation = manifestation;
    }

    public enum Condition {
        HR_THRESHOLD(
                "145021",
                List.of(new Source(SensorType.ANNE_CHEST, Metric.HR)),
                BigDecimal.valueOf(120.0),
                BigDecimal.valueOf(45.0),
                "hrthreshold"),
        RR_THRESHOLD(
                "145022",
                List.of(new Source(SensorType.ANNE_CHEST, Metric.RR_METRIC)),
                BigDecimal.valueOf(30.0),
                BigDecimal.valueOf(5.0),
                "rrthreshold");

        public final String code;
        public final List<Source> sources;
        public final BigDecimal upperLimit;
        public final BigDecimal lowerLimit;
        public final String handle;

        Condition(String code, List<Source> sources, BigDecimal upperLimit, BigDecimal lowerLimit, String handle) {
            this.handle = handle;
            this.sources = sources;
            this.code = code;
            this.upperLimit = upperLimit;
            this.lowerLimit = lowerLimit;
        }
    }

    public record Source(SensorType sensorType, Metric metric) {}
}
