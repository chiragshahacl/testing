package org.sibel.models.payloads;

public record PatientAdmissionRejectedPayload(String devicePrimaryIdentifier, String patientPrimaryIdentifier)
        implements PayloadInterface {}
