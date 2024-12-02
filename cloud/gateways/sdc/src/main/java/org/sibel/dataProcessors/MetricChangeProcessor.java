package org.sibel.dataProcessors;

import static org.sibel.mdib.MdibUtils.getParentDescriptorByClass;
import static org.sibel.mdib.MdibUtils.getValueFromProductionSpec;

import com.google.inject.Inject;
import com.google.inject.assistedinject.Assisted;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import org.apache.kafka.common.header.internals.RecordHeader;
import org.sibel.constants.KafkaHeaders;
import org.sibel.constants.ProductionSpecCodes;
import org.sibel.exceptions.ProcessingError;
import org.sibel.factories.InstantProvider;
import org.sibel.factories.UuidProvider;
import org.sibel.models.BrokerMessage;
import org.sibel.models.MetricBrokerMessage;
import org.sibel.models.payloads.MetricPayload;
import org.somda.sdc.biceps.common.access.MdibAccess;
import org.somda.sdc.biceps.model.participant.*;

public class MetricChangeProcessor {

    private final AbstractMetricState state;
    private final MdibAccess mdibAccess;
    private final String patientPrimaryIdentifier;
    private final UuidProvider uuidProvider;
    private final InstantProvider instantProvider;

    private VmdDescriptor deviceDescriptor = null;
    private AbstractMetricDescriptor metricDescriptor = null;

    @Inject
    public MetricChangeProcessor(
            @Assisted MdibAccess mdibAccess,
            @Assisted AbstractMetricState state,
            @Assisted String patientPrimaryIdentifier,
            UuidProvider uuidProvider,
            InstantProvider instantProvider) {
        this.state = state;
        this.mdibAccess = mdibAccess;
        this.patientPrimaryIdentifier = patientPrimaryIdentifier;
        this.uuidProvider = uuidProvider;
        this.instantProvider = instantProvider;
    }

    public MetricPayload<BigDecimal> getNumericMetricPayload() throws ProcessingError {
        var numericMetricState = (NumericMetricState) state;
        var metricQualityValidity =
                numericMetricState.getMetricValue().getMetricQuality().getValidity();
        if (metricQualityValidity == MeasurementValidity.VLD || metricQualityValidity == MeasurementValidity.VLDATED) {
            var value = numericMetricState.getMetricValue().getValue();
            var determinationTime = numericMetricState.getMetricValue().getDeterminationTime();
            ArrayList<BigDecimal> values = new ArrayList<>();
            values.add(value);
            return new MetricPayload<>(
                    patientPrimaryIdentifier,
                    values,
                    determinationTime,
                    getMetricCode(),
                    getUnitCode(),
                    getDeviceCode(),
                    getDevicePrimaryIdentifier());
        } else {
            throw new ProcessingError("Received message was not valid. Received quality is: " + metricQualityValidity);
        }
    }

    public MetricPayload<String> getStringMetricPayload() throws ProcessingError {
        var stringMetricState = (StringMetricState) state;
        var metricQualityValidity =
                stringMetricState.getMetricValue().getMetricQuality().getValidity();
        if (metricQualityValidity == MeasurementValidity.VLD || metricQualityValidity == MeasurementValidity.VLDATED) {
            var value = stringMetricState.getMetricValue().getValue();
            var determinationTime = stringMetricState.getMetricValue().getDeterminationTime();
            ArrayList<String> values = new ArrayList<>();
            values.add(value);
            return new MetricPayload<>(
                    patientPrimaryIdentifier,
                    values,
                    determinationTime,
                    getMetricCode(),
                    getDeviceCode(),
                    getDevicePrimaryIdentifier());
        } else {
            throw new ProcessingError("Received message was not valid. Received quality is: " + metricQualityValidity);
        }
    }

    public List<RecordHeader> getBrokerMessageHeaders() throws ProcessingError {
        return List.of(
                new RecordHeader(KafkaHeaders.CODE, getMetricCode().getBytes()),
                new RecordHeader(
                        KafkaHeaders.DEVICE_PRIMARY_IDENTIFIER,
                        getDevicePrimaryIdentifier().getBytes()));
    }

    public BrokerMessage getBrokerMessage() throws ProcessingError {
        try {
            if (state instanceof NumericMetricState) {
                return new MetricBrokerMessage<>(uuidProvider.get(), instantProvider.now(), getNumericMetricPayload());
            } else if (state instanceof StringMetricState) {
                return new MetricBrokerMessage<>(uuidProvider.get(), instantProvider.now(), getStringMetricPayload());
            }
        } catch (Exception e) {
            throw new ProcessingError("Unexpected error processing metric data", e);
        }
        throw new ProcessingError("Unsupported metric type %s for metric %s"
                .formatted(state.getClass().getName(), state.getDescriptorHandle()));
    }

    private String getDeviceCode() throws ProcessingError {
        return getValueFromProductionSpec(getDeviceDescriptor(), ProductionSpecCodes.DEVICE_CODE);
    }

    private String getDevicePrimaryIdentifier() throws ProcessingError {
        return getValueFromProductionSpec(getDeviceDescriptor(), ProductionSpecCodes.DEVICE_PRIMARY_IDENTIFIER);
    }

    private VmdDescriptor getDeviceDescriptor() throws ProcessingError {
        if (deviceDescriptor == null) {
            deviceDescriptor = getParentDescriptorByClass(mdibAccess, state, VmdDescriptor.class)
                    .orElseThrow(() -> new ProcessingError(
                            "No device descriptor found for metric %s".formatted(state.getDescriptorHandle())));
        }
        return deviceDescriptor;
    }

    private String getMetricCode() throws ProcessingError {
        return getMetricDescriptor().getType().getCode();
    }

    private String getUnitCode() throws ProcessingError {
        return getMetricDescriptor().getUnit().getCode();
    }

    private AbstractMetricDescriptor getMetricDescriptor() throws ProcessingError {
        if (metricDescriptor == null) {
            metricDescriptor = mdibAccess
                    .getDescriptor(state.getDescriptorHandle(), AbstractMetricDescriptor.class)
                    .orElseThrow(() -> new ProcessingError(
                            "No metric descriptor found for metric %s".formatted(state.getDescriptorHandle())));
        }
        return metricDescriptor;
    }
}
