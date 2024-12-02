package org.sibel.models;

import java.time.Instant;
import org.sibel.models.payloads.PatientSessionClosedPayload;

public class PatientSessionClosedBrokerMessage extends AbstractBrokerMessage {
    private static final String EVENT_NAME = "Patient session closed";

    private static final String EVENT_TYPE = "PATIENT_SESSION_CLOSED_EVENT";

    public PatientSessionClosedBrokerMessage(String messageId, Instant timestamp, PatientSessionClosedPayload payload) {
        super(messageId, EVENT_NAME, EVENT_TYPE, timestamp, payload);
        LOG.info(String.format("New event: %s", EVENT_TYPE));
    }
}
