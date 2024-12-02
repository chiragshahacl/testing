package org.sibel.dataProcessors;

import com.google.inject.Inject;
import com.google.inject.assistedinject.Assisted;
import java.math.BigDecimal;
import java.math.RoundingMode;
import org.sibel.exceptions.ProcessingError;
import org.sibel.models.payloads.internal.VitalsRangePayload;
import org.somda.sdc.biceps.common.access.MdibAccess;
import org.somda.sdc.biceps.model.participant.*;

public class VitalRangeProcessor {
    private final MdibAccess mdibAccess;
    private final LimitAlertConditionState state;

    @Inject
    public VitalRangeProcessor(@Assisted MdibAccess mdibAccess, @Assisted LimitAlertConditionState state) {
        this.mdibAccess = mdibAccess;
        this.state = state;
    }

    public VitalsRangePayload getVitalsRangePayload() throws ProcessingError {
        try {
            var descriptorHandle = state.getDescriptorHandle();
            var descriptor = mdibAccess
                    .getDescriptor(descriptorHandle, LimitAlertConditionDescriptor.class)
                    .orElseThrow(() ->
                            new ProcessingError("No descriptor found for vital range: %s".formatted(descriptorHandle)));
            var code = descriptor.getType().getCode();

            var defaultLimits = descriptor.getMaxLimits();
            BigDecimal defaultUpperLimit = null;
            BigDecimal defaultLowerLimit = null;
            if (defaultLimits != null) {
                defaultUpperLimit = defaultLimits.getUpper();
                defaultLowerLimit = defaultLimits.getLower();
            }

            var limits = state.getLimits();
            BigDecimal upperLimit = null;
            BigDecimal lowerLimit = null;
            if (limits != null) {
                upperLimit = limits.getUpper();
                lowerLimit = limits.getLower();
            }

            boolean alertConditionEnabled = state.getActivationState() == null
                    || state.getActivationState().equals(AlertActivation.ON);

            return new VitalsRangePayload(
                    code,
                    parseVitalRangeLimit(upperLimit, defaultUpperLimit),
                    parseVitalRangeLimit(lowerLimit, defaultLowerLimit),
                    alertConditionEnabled);
        } catch (Exception e) {
            throw new ProcessingError("Unexpected error processing vital ranges", e);
        }
    }

    private static BigDecimal parseVitalRangeLimit(BigDecimal value, BigDecimal defaultValue) {
        var actualValue = value != null ? value : defaultValue;
        return actualValue != null ? actualValue.setScale(1, RoundingMode.HALF_EVEN) : null;
    }
}
