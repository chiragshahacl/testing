package org.sibel.models;

import java.time.Instant;
import org.sibel.models.payloads.SensorRemovedPayload;

public class SensorRemovedBrokerMessage extends AbstractBrokerMessage {
    private static final String EVENT_NAME = "Sensor removed";

    private static final String EVENT_TYPE = "SENSOR_REMOVED_EVENT";

    public SensorRemovedBrokerMessage(String messageId, Instant timestamp, SensorRemovedPayload payload) {
        super(messageId, EVENT_NAME, EVENT_TYPE, timestamp, payload);
        LOG.info(String.format("New event: %s", EVENT_TYPE));
    }
}
