package org.sibel.models.events;

import java.time.Instant;
import org.sibel.models.Patient;

public class PatientSessionEndedEvent extends PatientUpdateEvent {
    public PatientSessionEndedEvent(String id, Instant timestamp, String pmId, String patientId, Patient patient) {
        super(EventType.PATIENT_SESSION_ENDED, id, timestamp, pmId, patientId, patient);
    }
}
