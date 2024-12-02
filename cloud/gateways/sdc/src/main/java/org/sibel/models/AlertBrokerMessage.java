package org.sibel.models;

import java.time.Instant;
import org.sibel.models.payloads.AlertPayload;
import org.sibel.models.payloads.PayloadInterface;

public class AlertBrokerMessage extends AbstractBrokerMessage {

    private static final String EVENT_NAME = "Alert update";
    private static final String EVENT_TYPE = "NEW_ALERT_OBSERVATION";

    public AlertBrokerMessage(String message_id, Instant timestamp, PayloadInterface payload) {
        super(message_id, EVENT_NAME, EVENT_TYPE, timestamp, payload);
        LOG.info(String.format("New event: %s", EVENT_TYPE));
    }

    public AlertPayload getPayload() {
        return (AlertPayload) super.getPayload();
    }
}
