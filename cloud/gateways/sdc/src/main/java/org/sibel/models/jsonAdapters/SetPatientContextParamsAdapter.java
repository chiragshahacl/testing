package org.sibel.models.jsonAdapters;

import com.google.gson.*;
import java.lang.reflect.Type;
import java.util.List;
import org.sibel.models.scoParams.SetPatientContextParams;
import org.somda.sdc.biceps.model.participant.ContextAssociation;
import org.somda.sdc.biceps.model.participant.Sex;

public class SetPatientContextParamsAdapter implements JsonDeserializer<SetPatientContextParams> {
    @Override
    public SetPatientContextParams deserialize(
            JsonElement jsonElement, Type type, JsonDeserializationContext jsonDeserializationContext)
            throws JsonParseException {
        try {
            JsonObject jsonObject = jsonElement.getAsJsonObject();

            var primaryIdentifier = jsonObject.get("primary_identifier").getAsString();
            var givenName = jsonObject.get("given_name").getAsString();
            var familyName = jsonObject.get("family_name").getAsString();
            Sex gender = jsonDeserializationContext.deserialize(jsonObject.get("gender"), Sex.class);
            var birthDate = jsonObject.get("birth_date").getAsString();

            return new SetPatientContextParams(List.of(new SetPatientContextParams.Patient(
                    primaryIdentifier, givenName, familyName, gender, birthDate, ContextAssociation.ASSOC)));
        } catch (Exception e) {
            throw new JsonParseException(e);
        }
    }
}
