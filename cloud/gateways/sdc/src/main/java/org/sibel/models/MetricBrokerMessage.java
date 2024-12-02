package org.sibel.models;

import java.time.Instant;
import org.sibel.models.payloads.MetricPayload;

public class MetricBrokerMessage<T> extends AbstractBrokerMessage {
    private static final String EVENT_NAME = "New metrics found";
    private static final String EVENT_TYPE = "NEW_METRICS";

    public MetricBrokerMessage(String message_id, Instant timestamp, MetricPayload<T> payload) {
        super(message_id, EVENT_NAME, EVENT_TYPE, timestamp, payload);
    }
}
