package org.sibel.dataProcessors;

import static org.sibel.mdib.MdibUtils.getParentDescriptorByClass;
import static org.sibel.mdib.MdibUtils.getValueFromProductionSpec;

import com.google.inject.Inject;
import com.google.inject.assistedinject.Assisted;
import java.time.Instant;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import org.apache.kafka.common.header.internals.RecordHeader;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.constants.KafkaHeaders;
import org.sibel.constants.ProductionSpecCodes;
import org.sibel.exceptions.ProcessingError;
import org.sibel.factories.InstantProvider;
import org.sibel.factories.ProcessorFactory;
import org.sibel.models.payloads.AlertPayload;
import org.sibel.models.payloads.internal.VitalsRangePayload;
import org.somda.sdc.biceps.common.access.MdibAccess;
import org.somda.sdc.biceps.model.participant.*;

public class AlertChangeProcessor {
    private static final Logger LOG = LogManager.getLogger();

    private final MdibAccess mdibAccess;
    private final AlertSignalState state;
    private final String gatewayId;
    private final String gatewayModelNumber;
    private final String patientPrimaryIdentifier;

    private AlertConditionDescriptor alertConditionDescriptor = null;
    private AlertConditionState alertConditionState = null;
    private boolean deviceDescriptorFetched = false;
    private VmdDescriptor deviceDescriptor = null;
    private AlertSignalDescriptor alertSignalDescriptor;
    private final InstantProvider instantProvider;
    private final ProcessorFactory processorFactory;

    @Inject
    public AlertChangeProcessor(
            @Assisted MdibAccess mdibAccess,
            @Assisted AlertSignalState state,
            @Assisted("gatewayId") String gatewayId,
            @Assisted("gatewayModelNumber") String gatewayModelNumber,
            @Assisted("patientPrimaryIdentifier") String patientPrimaryIdentifier,
            InstantProvider instantProvider,
            ProcessorFactory processorFactory) {
        this.mdibAccess = mdibAccess;
        this.state = state;
        this.gatewayId = gatewayId;
        this.gatewayModelNumber = gatewayModelNumber;
        this.patientPrimaryIdentifier = patientPrimaryIdentifier;
        this.instantProvider = instantProvider;
        this.processorFactory = processorFactory;
    }

    public String getCacheKey() throws ProcessingError {
        return String.format("%s-%s", state.getDescriptorHandle(), getSignalCode());
    }

    public AlertConditionKind getAlertKind() throws ProcessingError {
        return getAlertConditionDescriptor().getKind();
    }

    public AlertPayload getAlertSignalPayload() throws ProcessingError {
        try {
            return new AlertPayload(
                    patientPrimaryIdentifier,
                    isAlertActive() || isLatchingActive(),
                    isLatchingActive(),
                    getSignalCode(),
                    getDeviceCode(),
                    getAlertPriority(),
                    getDeterminationTime(),
                    getDevicePrimaryIdentifier(),
                    getAlertVitalRange());
        } catch (Exception e) {
            throw new ProcessingError("Unexpected error processing alert states", e);
        }
    }

    public List<RecordHeader> getHeaders() throws ProcessingError {
        return getAlertKind() == AlertConditionKind.TEC
                ? List.of(
                        new RecordHeader(KafkaHeaders.PATIENT_PRIMARY_IDENTIFIER, patientPrimaryIdentifier.getBytes()))
                : null;
    }

    private AlertSignalDescriptor getAlertSignalDescriptor() throws ProcessingError {
        if (alertSignalDescriptor == null) {
            alertSignalDescriptor = getParentDescriptorByClass(mdibAccess, state, AlertSignalDescriptor.class)
                    .orElseThrow(() -> new ProcessingError(
                            "No alert signal found for alarm: %s".formatted(state.getDescriptorHandle())));
        }
        return alertSignalDescriptor;
    }

    private boolean isAlertActive() throws ProcessingError {
        processAlertCondition();
        try {
            return alertConditionState != null
                    ? alertConditionState.isPresence()
                    : state.getPresence() == AlertSignalPresence.ON;
        } catch (NullPointerException e) {
            // If presence is null for the condition it throws an exception
            return state.getPresence() == AlertSignalPresence.ON;
        }
    }

    private boolean isLatchingActive() throws ProcessingError {
        processAlertCondition();
        try {
            if (alertConditionState != null && !alertConditionState.isPresence()) {
                return state.getPresence() == AlertSignalPresence.LATCH;
            } else {
                if (state.getPresence() == AlertSignalPresence.LATCH)
                    LOG.warn("Not a Valid condition - Conditaion presense and Latch can not be true at same time");
                return false;
            }
        } catch (Exception e) {
            // In case of exception we will be sending latch as false just for safty messure
            LOG.warn("Not a Valid condition ", e);
            return false;
        }
    }

    private String getSignalCode() throws ProcessingError {
        return getAlertSignalDescriptor().getType().getCode();
    }

    private String getDevicePrimaryIdentifier() throws ProcessingError {
        return getDeviceProductionSpec(ProductionSpecCodes.DEVICE_PRIMARY_IDENTIFIER)
                .orElse(gatewayId);
    }

    private String getDeviceCode() throws ProcessingError {
        return getDeviceProductionSpec(ProductionSpecCodes.DEVICE_CODE).orElse(gatewayModelNumber);
    }

    private Optional<String> getDeviceProductionSpec(String specCode) throws ProcessingError {
        if (!deviceDescriptorFetched) {
            var alertParentDevice = getParentDescriptorByClass(
                            mdibAccess, state, AbstractDeviceComponentDescriptor.class)
                    .orElse(null);
            if (alertParentDevice != null && VmdDescriptor.class.isAssignableFrom(alertParentDevice.getClass())) {
                deviceDescriptor = (VmdDescriptor) alertParentDevice;
            } else {
                var sourceHandleList = getAlertConditionDescriptor().getSource();
                deviceDescriptor = sourceHandleList.stream()
                        .map(sourceHandle -> getParentDescriptorByClass(mdibAccess, sourceHandle, VmdDescriptor.class))
                        .flatMap(Optional::stream)
                        .findFirst()
                        .orElse(null);
                var hasValidSources = sourceHandleList.stream()
                        .flatMap(sourceHandle -> mdibAccess.getEntity(sourceHandle).stream())
                        .findAny()
                        .isPresent();
                if (deviceDescriptor == null && !hasValidSources) {
                    throw new ProcessingError("Cannot obtain production spec from alert, no valid source metrics");
                }
            }
            deviceDescriptorFetched = true;
        }
        return deviceDescriptor != null
                ? Optional.ofNullable(getValueFromProductionSpec(deviceDescriptor, specCode))
                : Optional.empty();
    }

    private AlertConditionDescriptor getAlertConditionDescriptor() throws ProcessingError {
        processAlertCondition();
        return alertConditionDescriptor;
    }

    private void processAlertCondition() throws ProcessingError {
        if (alertConditionDescriptor == null) {
            var alertSystem = getParentDescriptorByClass(mdibAccess, state, AlertSystemDescriptor.class)
                    .orElseThrow(() -> new ProcessingError(
                            "No alert system found for alarm %s".formatted(state.getDescriptorHandle())));
            var signalDescriptor = getAlertSignalDescriptor();
            var entity = mdibAccess.getChildrenByType(alertSystem.getHandle(), AlertConditionDescriptor.class).stream()
                    .filter(alertConditionEntity ->
                            alertConditionEntity.getHandle().equals(signalDescriptor.getConditionSignaled()))
                    .findFirst()
                    .orElseThrow(() -> new ProcessingError(
                            "No alert condition found for alarm %s".formatted(state.getDescriptorHandle())));
            alertConditionDescriptor = (AlertConditionDescriptor) entity.getDescriptor();
            alertConditionState =
                    entity.getFirstState(LimitAlertConditionState.class).orElse(null);
        }
    }

    private String getAlertPriority() throws ProcessingError {
        return getAlertConditionDescriptor().getPriority().toString();
    }

    private Instant getDeterminationTimeFromStringMetric(StringMetricState state) {
        var metricValue = state.getMetricValue();
        return metricValue != null ? metricValue.getDeterminationTime() : this.instantProvider.now();
    }

    private Instant getDeterminationTimeFromNumericMetric(NumericMetricState state) {
        var determinationTime = this.instantProvider.now();
        try {
            var metricValue = state.getMetricValue();
            if (metricValue != null) {
                determinationTime = metricValue.getDeterminationTime();
            }
        } catch (NullPointerException e) {
            determinationTime = this.instantProvider.now();
        }
        return determinationTime;
    }

    private Instant getDeterminationTime() throws ProcessingError {
        var determinationTime = mdibAccess
                .getState(getAlertConditionDescriptor().getHandle(), AlertConditionState.class)
                .map(AlertConditionState::getDeterminationTime)
                .orElse(null);

        if (determinationTime == null) {
            determinationTime = getAlertConditionDescriptor().getSource().stream()
                    .map(mdibAccess::getState)
                    .flatMap(Optional::stream)
                    .map(source -> {
                        if (source instanceof StringMetricState) {
                            return getDeterminationTimeFromStringMetric((StringMetricState) source);
                        } else if (source instanceof NumericMetricState) {
                            return getDeterminationTimeFromNumericMetric((NumericMetricState) source);
                        }
                        return null;
                    })
                    .filter(Objects::nonNull)
                    .findFirst()
                    .orElse(null);
        }

        if (determinationTime == null) {
            LOG.warn("No determination time found for alert with handle: {}", state.getDescriptorHandle());
            determinationTime = instantProvider.now();
        }

        return determinationTime;
    }

    private VitalsRangePayload getAlertVitalRange() throws ProcessingError {
        processAlertCondition();
        LimitAlertConditionState limitAlertConditionState = null;
        try {
            limitAlertConditionState = (LimitAlertConditionState) alertConditionState;
        } catch (Exception e) {
            LOG.warn("Failed to cast alert condition state to LimitAlertConditionState", e);
        }
        return limitAlertConditionState != null
                ? processorFactory
                        .createVitalRangeProcessor(mdibAccess, limitAlertConditionState)
                        .getVitalsRangePayload()
                : null;
    }
}
