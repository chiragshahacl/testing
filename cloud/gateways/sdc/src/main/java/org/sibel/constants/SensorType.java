package org.sibel.constants;

public enum SensorType {
    PM("Patient Monitor", "pm"),
    ANNE_CHEST("ANNE Chest", "annechest"),
    ANNE_LIMB("ANNE Limb", "annelimb");

    public final String code;
    public final String handle;

    SensorType(String code, String handle) {
        this.code = code;
        this.handle = handle;
    }
}
