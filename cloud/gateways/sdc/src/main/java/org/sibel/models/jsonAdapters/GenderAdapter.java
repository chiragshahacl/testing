package org.sibel.models.jsonAdapters;

import com.google.gson.*;
import java.lang.reflect.Type;
import org.sibel.models.Gender;

public class GenderAdapter implements JsonSerializer<Gender>, JsonDeserializer<Gender> {
    @Override
    public Gender deserialize(JsonElement jsonElement, Type type, JsonDeserializationContext jsonDeserializationContext)
            throws JsonParseException {
        return Gender.fromFhirGenderConcept(jsonElement.getAsString());
    }

    @Override
    public JsonElement serialize(Gender gender, Type type, JsonSerializationContext jsonSerializationContext) {
        return new JsonPrimitive(gender.getFhirGenderConcept());
    }
}
