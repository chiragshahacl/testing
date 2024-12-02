package org.sibel.models;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.google.gson.Gson;
import com.google.inject.Guice;
import org.junit.jupiter.api.BeforeEach;
import org.sibel.di.TestModule;

public class SerializationTest {
    private Gson gson;

    @BeforeEach
    void setUp() {
        var injector = Guice.createInjector(new TestModule());
        gson = injector.getInstance(Gson.class);
    }

    protected void assertObjectSerialized(Object modelInstance, String expectedJson) {
        assertEquals(expectedJson, gson.toJson(modelInstance));
    }

    protected void assertObjectDeserialized(Object expectedModelInstance, Class<?> model, String rawJson) {
        assertEquals(expectedModelInstance, gson.fromJson(rawJson, model));
    }
}
