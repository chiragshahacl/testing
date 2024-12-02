package org.sibel.models;

import java.time.Instant;
import org.sibel.models.payloads.WaveformPayload;

public class WaveformBrokerMessage extends AbstractBrokerMessage {
    private static final String EVENT_NAME = "New waveform vitals";
    private static final String EVENT_TYPE = "NEW_WAVEFORM_VITALS";

    public WaveformBrokerMessage(String message_id, Instant timestamp, WaveformPayload payload) {
        super(message_id, EVENT_NAME, EVENT_TYPE, timestamp, payload);
    }
}
