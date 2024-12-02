package org.sibel.models.jsonAdapters;

import com.google.gson.*;
import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.List;
import javax.xml.namespace.QName;
import org.somda.sdc.dpws.client.DiscoveredDevice;

public class DiscoveredDeviceAdapter implements JsonSerializer<DiscoveredDevice>, JsonDeserializer<DiscoveredDevice> {
    @Override
    public JsonElement serialize(
            DiscoveredDevice discoveredDevice, Type type, JsonSerializationContext jsonSerializationContext) {
        var jsonTypes = new JsonArray();
        discoveredDevice.getTypes().forEach(qName -> {
            var jsonQname = new JsonObject();
            jsonQname.addProperty("namespaceURI", qName.getNamespaceURI());
            jsonQname.addProperty("localPart", qName.getLocalPart());
            jsonQname.addProperty("prefix", qName.getPrefix());
            jsonTypes.add(jsonQname);
        });

        var jsonPayload = new JsonObject();
        jsonPayload.addProperty("eprAddress", discoveredDevice.getEprAddress());
        jsonPayload.add("types", jsonTypes);
        jsonPayload.add("scopes", jsonSerializationContext.serialize(discoveredDevice.getScopes()));
        jsonPayload.add("xAddrs", jsonSerializationContext.serialize(discoveredDevice.getXAddrs()));
        jsonPayload.addProperty("metadataVersion", discoveredDevice.getMetadataVersion());
        return jsonPayload;
    }

    @Override
    public DiscoveredDevice deserialize(
            JsonElement jsonElement, Type type, JsonDeserializationContext jsonDeserializationContext)
            throws JsonParseException {
        var jsonPayload = jsonElement.getAsJsonObject();
        var eprAddress = jsonPayload.get("eprAddress").getAsString();
        var types = jsonPayload.get("types").getAsJsonArray().asList().stream()
                .map(jsonQnameElement -> {
                    var jsonQname = jsonQnameElement.getAsJsonObject();
                    var namespaceURI = jsonQname.get("namespaceURI").getAsString();
                    var localPart = jsonQname.get("localPart").getAsString();
                    var prefix = jsonQname.get("prefix").getAsString();
                    return new QName(namespaceURI, localPart, prefix);
                })
                .toList();
        List<String> scopes = jsonDeserializationContext.deserialize(jsonPayload.get("scopes"), ArrayList.class);
        List<String> xAddrs = jsonDeserializationContext.deserialize(jsonPayload.get("xAddrs"), ArrayList.class);
        var metadataVersion = jsonPayload.get("metadataVersion").getAsLong();

        return new DiscoveredDevice(eprAddress, types, scopes, xAddrs, metadataVersion);
    }
}
