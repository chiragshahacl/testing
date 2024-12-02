package org.sibel.dataProcessors.utils;

public interface Cache<T> {
    boolean hasChanged(String patientId, String key, T value);

    void addOrUpdate(String patientId, String key, T value);
}
