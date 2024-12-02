package org.sibel.models;

import java.time.Instant;
import org.sibel.models.payloads.PayloadInterface;

public class PatientAdmissionRejectedBrokerMessage extends AbstractBrokerMessage {
    private static final String EVENT_NAME = "Patient admission rejected";
    private static final String EVENT_TYPE = "PATIENT_ADMISSION_REJECTED";

    public PatientAdmissionRejectedBrokerMessage(String messageId, Instant timestamp, PayloadInterface payload) {
        super(messageId, EVENT_NAME, EVENT_TYPE, timestamp, payload);
    }
}
