package org.sibel.models;

import java.time.Instant;
import org.sibel.models.payloads.RealtimeStatePayload;

public class RealtimeStateBrokerMessage extends AbstractBrokerMessage {

    private static final String EVENT_NAME = "PM connection status";
    private static final String EVENT_TYPE = "PM_CONNECTION_STATUS_REPORT";

    public RealtimeStateBrokerMessage(String messageId, Instant timestamp, RealtimeStatePayload payload) {
        super(messageId, EVENT_NAME, EVENT_TYPE, timestamp, payload);
    }
}
