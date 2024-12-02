package org.sibel.dataProcessors.utils;

public class NoCache<T> implements Cache<T> {
    @Override
    public boolean hasChanged(String patientId, String key, T value) {
        return true;
    }

    @Override
    public void addOrUpdate(String patientId, String key, T value) {}
}
