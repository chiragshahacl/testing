package org.sibel.models;

import java.time.Instant;
import org.sibel.models.payloads.NewVitalsRangesPayload;

public class NewVitalsRangesBrokerMessage extends AbstractBrokerMessage {
    private static final String EVENT_NAME = "Device new vitals ranges added";
    private static final String EVENT_TYPE = "DEVICE_NEW_VITALS_RANGES";

    public NewVitalsRangesBrokerMessage(String messageId, Instant timestamp, NewVitalsRangesPayload payload) {
        super(messageId, EVENT_NAME, EVENT_TYPE, timestamp, payload);
        LOG.info(String.format("New event: %s", EVENT_TYPE));
    }
}
