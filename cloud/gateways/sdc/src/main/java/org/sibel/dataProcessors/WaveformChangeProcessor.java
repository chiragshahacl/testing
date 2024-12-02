package org.sibel.dataProcessors;

import static org.sibel.mdib.MdibUtils.getParentDescriptorByClass;
import static org.sibel.mdib.MdibUtils.getValueFromProductionSpec;

import com.google.inject.Inject;
import com.google.inject.assistedinject.Assisted;
import java.math.BigDecimal;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import org.apache.kafka.common.header.internals.RecordHeader;
import org.sibel.config.Settings;
import org.sibel.constants.KafkaHeaders;
import org.sibel.constants.ProductionSpecCodes;
import org.sibel.exceptions.ProcessingError;
import org.sibel.factories.InstantProvider;
import org.sibel.factories.UuidProvider;
import org.sibel.models.BrokerMessage;
import org.sibel.models.WaveformBrokerMessage;
import org.sibel.models.payloads.WaveformPayload;
import org.somda.sdc.biceps.common.access.MdibAccess;
import org.somda.sdc.biceps.model.participant.*;

public class WaveformChangeProcessor {

    private final RealTimeSampleArrayMetricState state;
    private final MdibAccess mdibAccess;
    private final String patientPrimaryIdentifier;
    private final Settings settings;
    private final UuidProvider uuidProvider;
    private final InstantProvider instantProvider;

    private RealTimeSampleArrayMetricDescriptor sampleDescriptor = null;
    private VmdDescriptor deviceDescriptor = null;

    @Inject
    public WaveformChangeProcessor(
            @Assisted MdibAccess mdibAccess,
            @Assisted RealTimeSampleArrayMetricState state,
            @Assisted String patientPrimaryIdentifier,
            Settings settings,
            UuidProvider uuidProvider,
            InstantProvider instantProvider) {
        this.state = state;
        this.mdibAccess = mdibAccess;
        this.patientPrimaryIdentifier = patientPrimaryIdentifier;
        this.settings = settings;
        this.uuidProvider = uuidProvider;
        this.instantProvider = instantProvider;
    }

    public BrokerMessage getBrokerMessage() throws ProcessingError {
        try {
            var payload = new WaveformPayload(
                    patientPrimaryIdentifier,
                    getWaveformSamples(),
                    getDeterminationTime(),
                    getWaveformSamplePeriod(),
                    getWaveformDeterminationPeriod(),
                    getWaveformCode(),
                    getDeviceCode(),
                    getDevicePrimaryIdentifier());
            return new WaveformBrokerMessage(uuidProvider.get(), instantProvider.now(), payload);
        } catch (Exception e) {
            throw new ProcessingError("Unexpected error processing waveform data", e);
        }
    }

    private String getDeviceCode() throws ProcessingError {
        return getValueFromProductionSpec(getDeviceDescriptor(), ProductionSpecCodes.DEVICE_CODE);
    }

    private String getDevicePrimaryIdentifier() throws ProcessingError {
        return getValueFromProductionSpec(getDeviceDescriptor(), ProductionSpecCodes.DEVICE_PRIMARY_IDENTIFIER);
    }

    private Duration getWaveformSamplePeriod() throws ProcessingError {
        return getRealTimeSampleDescriptor().getSamplePeriod();
    }

    private Duration getWaveformDeterminationPeriod() throws ProcessingError {
        if (settings.FEATURE_DETERMINATION_PERIOD_ENABLED()) {
            return getRealTimeSampleDescriptor().getDeterminationPeriod();
        }
        return Duration.ofMillis(500);
    }

    private String getWaveformCode() throws ProcessingError {
        return getRealTimeSampleDescriptor().getType().getCode();
    }

    private List<BigDecimal> getWaveformSamples() {
        return state.getMetricValue().getSamples();
    }

    private Instant getDeterminationTime() {
        return state.getMetricValue().getDeterminationTime();
    }

    private RealTimeSampleArrayMetricDescriptor getRealTimeSampleDescriptor() throws ProcessingError {
        if (sampleDescriptor == null) {
            sampleDescriptor = (RealTimeSampleArrayMetricDescriptor) mdibAccess
                    .getDescriptor(state.getDescriptorHandle())
                    .orElseThrow(() -> new ProcessingError("No sample descriptor found for waveform metric: %s"
                            .formatted(state.getDescriptorHandle())));
        }
        return sampleDescriptor;
    }

    private VmdDescriptor getDeviceDescriptor() throws ProcessingError {
        if (deviceDescriptor == null) {
            deviceDescriptor = getParentDescriptorByClass(mdibAccess, state, VmdDescriptor.class)
                    .orElseThrow(() -> new ProcessingError("No device descriptor found for waveform metric: %s"
                            .formatted(state.getDescriptorHandle())));
        }
        return deviceDescriptor;
    }

    public List<RecordHeader> getHeaders() throws ProcessingError {
        var headers = new ArrayList<RecordHeader>();
        headers.add(new RecordHeader(KafkaHeaders.CODE, getWaveformCode().getBytes()));
        headers.add(new RecordHeader(
                KafkaHeaders.DEVICE_PRIMARY_IDENTIFIER,
                getDevicePrimaryIdentifier().getBytes()));
        return headers;
    }
}
