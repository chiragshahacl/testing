package org.sibel.models.jsonAdapters;

import com.google.gson.JsonElement;
import com.google.gson.JsonPrimitive;
import com.google.gson.JsonSerializationContext;
import com.google.gson.JsonSerializer;
import java.lang.reflect.Type;
import org.sibel.constants.SensorType;

public class SensorTypeAdapter implements JsonSerializer<SensorType> {
    @Override
    public JsonElement serialize(SensorType sensorType, Type type, JsonSerializationContext jsonSerializationContext) {
        return new JsonPrimitive(sensorType.code);
    }
}
