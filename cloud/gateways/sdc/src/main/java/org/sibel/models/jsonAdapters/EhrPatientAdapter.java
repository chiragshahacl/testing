package org.sibel.models.jsonAdapters;

import com.google.gson.*;
import java.lang.reflect.Type;
import org.sibel.models.api.EhrPatient;

public class EhrPatientAdapter implements JsonDeserializer<EhrPatient> {
    @Override
    public EhrPatient deserialize(
            JsonElement jsonElement, Type type, JsonDeserializationContext jsonDeserializationContext)
            throws JsonParseException {
        var jsonObject = jsonElement.getAsJsonObject();
        var rawPatientIdentifiers = jsonObject.get("patientIdentifiers");
        if (rawPatientIdentifiers == null) {
            throw new JsonParseException("Field required: 'patientIdentifiers'.");
        }
        return new EhrPatient(
                rawPatientIdentifiers.getAsJsonArray().asList().stream()
                        .map(JsonElement::getAsString)
                        .toList(),
                getAsStringSafe(jsonObject.get("givenName")),
                getAsStringSafe(jsonObject.get("familyName")),
                getAsStringSafe(jsonObject.get("birthDate")),
                getAsStringSafe(jsonObject.get("gender")));
    }

    private static String getAsStringSafe(JsonElement rawValue) {
        return rawValue != null ? rawValue.getAsString() : null;
    }
}
