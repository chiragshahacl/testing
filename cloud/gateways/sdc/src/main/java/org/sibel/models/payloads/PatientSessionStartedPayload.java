package org.sibel.models.payloads;

import org.sibel.models.payloads.internal.PatientPayload;

public record PatientSessionStartedPayload(String patientMonitorIdentifier, PatientPayload patient)
        implements PayloadInterface {}
