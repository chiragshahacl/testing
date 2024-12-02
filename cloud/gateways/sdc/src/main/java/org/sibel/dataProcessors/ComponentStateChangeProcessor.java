package org.sibel.dataProcessors;

import static org.sibel.mdib.MdibUtils.getValueFromProductionSpec;

import com.google.inject.Inject;
import com.google.inject.assistedinject.Assisted;
import java.math.BigDecimal;
import java.util.List;
import org.apache.kafka.common.header.internals.RecordHeader;
import org.sibel.constants.KafkaHeaders;
import org.sibel.constants.ProductionSpecCodes;
import org.sibel.constants.UnitCodes;
import org.sibel.exceptions.ProcessingError;
import org.sibel.factories.InstantProvider;
import org.sibel.factories.UuidProvider;
import org.sibel.models.BrokerMessage;
import org.sibel.models.MetricBrokerMessage;
import org.sibel.models.payloads.MetricPayload;
import org.somda.sdc.biceps.common.access.MdibAccess;
import org.somda.sdc.biceps.model.participant.*;

public class ComponentStateChangeProcessor {

    private final AbstractDeviceComponentState state;
    private final MdibAccess mdibAccess;
    private final String gatewayId;
    private final String patientPrimaryIdentifier;
    private final UuidProvider uuidProvider;
    private final InstantProvider instantProvider;

    @Inject
    public ComponentStateChangeProcessor(
            @Assisted MdibAccess mdibAccess,
            @Assisted AbstractDeviceComponentState state,
            @Assisted("gatewayId") String gatewayId,
            @Assisted("patientPrimaryIdentifier") String patientPrimaryIdentifier,
            UuidProvider uuidProvider,
            InstantProvider instantProvider) {
        this.state = state;
        this.mdibAccess = mdibAccess;
        this.gatewayId = gatewayId;
        this.patientPrimaryIdentifier = patientPrimaryIdentifier;
        this.uuidProvider = uuidProvider;
        this.instantProvider = instantProvider;
    }

    public List<RecordHeader> getBatteryMessageHeaders() {
        return List.of(
                new RecordHeader(KafkaHeaders.CODE, getMetricCode().getBytes()),
                new RecordHeader(
                        KafkaHeaders.DEVICE_PRIMARY_IDENTIFIER,
                        getDevicePrimaryIdentifier().getBytes()));
    }

    public List<RecordHeader> getBatteryStatusMessageHeaders() {
        return List.of(
                new RecordHeader(KafkaHeaders.CODE, getChargingStatusCode().getBytes()),
                new RecordHeader(
                        KafkaHeaders.DEVICE_PRIMARY_IDENTIFIER,
                        getDevicePrimaryIdentifier().getBytes()));
    }

    public BrokerMessage getBatteryBrokerMessage() throws ProcessingError {
        try {
            return new MetricBrokerMessage<>(
                    uuidProvider.get(),
                    instantProvider.now(),
                    new MetricPayload<>(
                            patientPrimaryIdentifier,
                            getBatteryMetricValues(),
                            instantProvider.now(),
                            getMetricCode(),
                            getBatteryMetricUnitCode(),
                            getDeviceCode(),
                            getDevicePrimaryIdentifier()));
        } catch (Exception e) {
            throw new ProcessingError("Unexpected error processing battery state", e);
        }
    }

    public BrokerMessage getBatteryChargingStatusBrokerMessage() throws ProcessingError {
        try {
            return new MetricBrokerMessage<>(
                    uuidProvider.get(),
                    instantProvider.now(),
                    new MetricPayload<>(
                            patientPrimaryIdentifier,
                            getBatteryChargingStatus(),
                            instantProvider.now(),
                            getChargingStatusCode(),
                            UnitCodes.NO_UNIT, // The status does not have unit
                            getDeviceCode(),
                            getDevicePrimaryIdentifier()));
        } catch (Exception e) {
            throw new ProcessingError("Unexpected error processing battery charging status", e);
        }
    }

    private String getDescriptionHandle() {
        return state.getDescriptorHandle();
    }

    private AbstractDescriptor getHandleDescriptor() {
        return mdibAccess
                .getDescriptor(getDescriptionHandle())
                .orElseThrow(() -> new RuntimeException("Handle descriptor not available"));
    }

    private AbstractDeviceComponentDescriptor getDeviceDescriptor() {
        return mdibAccess
                .getEntity(getDescriptionHandle())
                .flatMap(entity -> entity.getDescriptor(AbstractDeviceComponentDescriptor.class))
                .orElseThrow(() -> new RuntimeException("Device descriptor not available"));
    }

    private String getDevicePrimaryIdentifier() {
        var deviceDescriptor = getDeviceDescriptor();
        if (deviceDescriptor.getClass().equals(MdsDescriptor.class)) {
            return gatewayId;
        } else {
            return getValueFromProductionSpec(deviceDescriptor, ProductionSpecCodes.DEVICE_PRIMARY_IDENTIFIER);
        }
    }

    private String getDeviceCode() {
        return getValueFromProductionSpec(getDeviceDescriptor(), ProductionSpecCodes.DEVICE_CODE);
    }

    private String getMetricCode() {
        return getHandleDescriptor().getType().getCode();
    }

    private String getChargingStatusCode() {
        return "%s-S".formatted(getHandleDescriptor().getType().getCode());
    }

    private Measurement getBatteryInformation() {
        return ((BatteryState) state).getCapacityRemaining();
    }

    private String getBatteryMetricUnitCode() {
        return getBatteryInformation().getMeasurementUnit().getCode();
    }

    private List<BigDecimal> getBatteryMetricValues() {
        return List.of(getBatteryInformation().getMeasuredValue());
    }

    private List<String> getBatteryChargingStatus() {
        var chargeStatus = ((BatteryState) state).getChargeStatus();
        return List.of(chargeStatus != null ? chargeStatus.value() : BatteryState.ChargeStatus.DIS_CH_B.value());
    }
}
