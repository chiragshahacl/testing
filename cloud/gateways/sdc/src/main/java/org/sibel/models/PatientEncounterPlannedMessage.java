package org.sibel.models;

public record PatientEncounterPlannedMessage(EventState eventState) {
    public record Device(String primaryIdentifier) {}

    public record Patient(
            String primaryIdentifier, String givenName, String familyName, String gender, String birthDate) {}

    public record EventState(Device device, Patient patient) {}

    public String pmId() {
        String pmId = null;
        if (eventState != null && eventState.device != null) {
            pmId = eventState.device().primaryIdentifier();
        }
        return pmId;
    }
}
