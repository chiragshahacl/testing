package org.sibel.models.jsonAdapters;

import com.google.gson.JsonDeserializationContext;
import com.google.gson.JsonDeserializer;
import com.google.gson.JsonElement;
import com.google.gson.JsonParseException;
import java.lang.reflect.Type;
import org.somda.sdc.biceps.model.participant.Sex;

public class SexAdapter implements JsonDeserializer<Sex> {
    public static final String MALE_TEXT = "male";
    public static final String FEMALE_TEXT = "female";
    public static final String OTHER_TEXT = "other";

    @Override
    public Sex deserialize(JsonElement jsonElement, Type type, JsonDeserializationContext jsonDeserializationContext)
            throws JsonParseException {
        var sexText = jsonElement.getAsString();
        return switch (sexText.toLowerCase()) {
            case MALE_TEXT -> Sex.M;
            case FEMALE_TEXT -> Sex.F;
            case OTHER_TEXT -> Sex.UNSPEC;
            default -> Sex.UNKN;
        };
    }
}
