package org.sibel.models;

import java.time.Instant;
import org.sibel.models.payloads.PayloadInterface;
import org.sibel.models.payloads.PmConfigurationUpdatedPayload;

public class PmConfigurationUpdatedBrokerMessage extends AbstractBrokerMessage {

    private static final String EVENT_NAME = "PM configuration updated";
    private static final String EVENT_TYPE = "PM_CONFIGURATION_UPDATED";

    public PmConfigurationUpdatedBrokerMessage(String messageId, Instant timestamp, PayloadInterface payload) {
        super(messageId, EVENT_NAME, EVENT_TYPE, timestamp, payload);
        LOG.info(String.format("New event: %s", EVENT_TYPE));
    }

    public PmConfigurationUpdatedPayload getPayload() {
        return (PmConfigurationUpdatedPayload) super.getPayload();
    }
}
