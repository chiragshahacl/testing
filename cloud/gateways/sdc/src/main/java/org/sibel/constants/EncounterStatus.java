package org.sibel.constants;

public enum EncounterStatus {
    PLANNED("planned"),
    IN_PROGRESS("in-progress"),
    COMPLETED("completed"),
    CANCELLED("cancelled");

    private final String value;

    EncounterStatus(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }
}
