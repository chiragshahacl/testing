package org.sibel.models.events;

import java.time.Instant;
import org.sibel.models.Patient;

public class PatientRejectedEvent extends PatientUpdateEvent {
    public PatientRejectedEvent(String id, Instant timestamp, String pmId, String patientId, Patient patient) {
        super(EventType.PATIENT_REJECTED, id, timestamp, pmId, patientId, patient);
    }
}
