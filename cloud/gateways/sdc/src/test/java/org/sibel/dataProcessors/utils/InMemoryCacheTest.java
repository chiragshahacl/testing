package org.sibel.dataProcessors.utils;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class InMemoryCacheTest {
    @Test
    void testCache() {
        var cache = new InMemoryCache<String>();
        var patientId = "john_doe";

        cache.addOrUpdate(patientId, "key", "value");

        assertTrue(cache.hasChanged(patientId, "non_existing_key", "fake_value"));
        assertTrue(cache.hasChanged(patientId, "key", "new_value"));
        assertFalse(cache.hasChanged(patientId, "key", "value"));
    }
}
