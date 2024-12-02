package org.sibel.models;

import java.time.Instant;
import org.sibel.models.payloads.PayloadInterface;

public class PatientSessionStartedBrokerMessage extends AbstractBrokerMessage {
    private static final String EVENT_NAME = "Patient session started";
    private static final String EVENT_TYPE = "PATIENT_SESSION_STARTED";

    public PatientSessionStartedBrokerMessage(String messageId, Instant timestamp, PayloadInterface payload) {
        super(messageId, EVENT_NAME, EVENT_TYPE, timestamp, payload);
    }
}
