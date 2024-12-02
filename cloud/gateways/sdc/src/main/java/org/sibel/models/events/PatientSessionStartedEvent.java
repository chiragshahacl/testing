package org.sibel.models.events;

import java.time.Instant;
import org.sibel.models.Patient;

public class PatientSessionStartedEvent extends PatientUpdateEvent {
    public PatientSessionStartedEvent(String id, Instant timestamp, String pmId, String patientId, Patient patient) {
        super(EventType.PATIENT_SESSION_STARTED, id, timestamp, pmId, patientId, patient);
    }
}
