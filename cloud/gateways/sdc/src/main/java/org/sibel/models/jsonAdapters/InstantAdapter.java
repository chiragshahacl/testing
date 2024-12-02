package org.sibel.models.jsonAdapters;

import com.google.gson.*;
import java.lang.reflect.Type;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;

public class InstantAdapter implements JsonSerializer<Instant>, JsonDeserializer<Instant> {
    private final DateTimeFormatter formatter;

    public InstantAdapter() {
        this.formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSS");
    }

    @Override
    public JsonElement serialize(Instant timestamp, Type type, JsonSerializationContext jsonSerializationContext) {
        return new JsonPrimitive(formatter.format(timestamp.atOffset(ZoneOffset.UTC)));
    }

    @Override
    public Instant deserialize(
            JsonElement jsonElement, Type type, JsonDeserializationContext jsonDeserializationContext)
            throws JsonParseException {
        var localDateTime = LocalDateTime.parse(jsonElement.getAsString(), formatter);
        return localDateTime.atOffset(ZoneOffset.UTC).toInstant();
    }
}
