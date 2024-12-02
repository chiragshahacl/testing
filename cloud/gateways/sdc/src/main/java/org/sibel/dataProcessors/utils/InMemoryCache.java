package org.sibel.dataProcessors.utils;

import java.util.HashMap;

public class InMemoryCache<T> implements Cache<T> {
    private final HashMap<String, HashMap<String, T>> cache = new HashMap<>();

    @Override
    public boolean hasChanged(String patientId, String key, T value) {
        cache.putIfAbsent(patientId, new HashMap<>());
        var patientCache = cache.get(patientId);
        var cachedValue = patientCache.get(key);
        return cachedValue == null || !cachedValue.equals(value);
    }

    @Override
    public void addOrUpdate(String patientId, String key, T value) {
        cache.putIfAbsent(patientId, new HashMap<>());
        var patientCache = cache.get(patientId);
        patientCache.put(key, value);
    }
}
