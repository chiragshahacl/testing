package org.sibel.models.jsonAdapters;

import com.google.gson.JsonDeserializationContext;
import com.google.gson.JsonDeserializer;
import com.google.gson.JsonElement;
import com.google.gson.JsonParseException;
import java.lang.reflect.Type;
import java.time.Instant;
import org.sibel.models.CommandEventBrokerMessage;

public class CommandEventBrokerMessageAdapter implements JsonDeserializer<CommandEventBrokerMessage> {
    @Override
    public CommandEventBrokerMessage deserialize(
            JsonElement jsonElement, Type type, JsonDeserializationContext jsonDeserializationContext)
            throws JsonParseException {
        try {
            var jsonObject = jsonElement.getAsJsonObject();

            var eventName = jsonObject.get("event_name").getAsString();
            var entityId = jsonObject.get("entity_id").getAsString();
            var performedOn =
                    (Instant) jsonDeserializationContext.deserialize(jsonObject.get("performed_on"), Instant.class);
            var performedBy = jsonObject.get("performed_by").getAsString();
            var entityName = jsonObject.get("entity_name").getAsString();
            var emittedBy = jsonObject.get("emitted_by").getAsString();
            var eventType = jsonObject.get("event_type").getAsString();
            var messageId = jsonObject.get("message_id").getAsString();

            var eventState = jsonObject.get("event_state").getAsJsonObject();
            var commandName = eventState.get("command_name").getAsString();
            var pmIdentifier = eventState.get("pm_identifier").getAsString();
            var requestId = eventState.get("request_id").getAsString();
            var rawJsonParams = eventState.get("params").toString();

            return new CommandEventBrokerMessage(
                    entityId,
                    eventName,
                    commandName,
                    pmIdentifier,
                    requestId,
                    performedOn,
                    performedBy,
                    entityName,
                    emittedBy,
                    eventType,
                    messageId,
                    rawJsonParams);
        } catch (Exception e) {
            throw new JsonParseException(
                    "Failed to parse \"%s\" as a CommandEventBrokerMessage".formatted(jsonElement), e);
        }
    }
}
