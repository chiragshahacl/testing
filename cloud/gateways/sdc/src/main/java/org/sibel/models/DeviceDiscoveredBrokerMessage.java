package org.sibel.models;

import java.time.Instant;
import org.sibel.models.payloads.DeviceDiscoveredPayload;

public class DeviceDiscoveredBrokerMessage extends AbstractBrokerMessage {
    private static final String EVENT_NAME = "Device discovered";

    private static final String EVENT_TYPE = "DEVICE_DISCOVERED";

    public DeviceDiscoveredBrokerMessage(String messageId, Instant timestamp, DeviceDiscoveredPayload payload) {
        super(messageId, EVENT_NAME, EVENT_TYPE, timestamp, payload);
        LOG.info(String.format("New event: %s", EVENT_TYPE));
    }
}
