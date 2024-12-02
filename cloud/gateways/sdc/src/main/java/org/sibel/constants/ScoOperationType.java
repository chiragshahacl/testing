package org.sibel.constants;

import static org.sibel.constants.MdibHandles.PATIENT_CONTEXT_HANDLE;

public enum ScoOperationType {
    SET_CONTEXT_STATE("setPatientContext", PATIENT_CONTEXT_HANDLE);

    public final String handle;
    public final String target;

    ScoOperationType(String handle, String target) {
        this.handle = handle;
        this.target = target;
    }
}
