package org.sibel.jsonAdapters;

import static org.junit.jupiter.api.Assertions.*;

import com.google.gson.FieldNamingPolicy;
import com.google.gson.GsonBuilder;
import java.util.List;
import javax.xml.namespace.QName;
import org.junit.jupiter.api.Test;
import org.sibel.models.jsonAdapters.DiscoveredDeviceAdapter;
import org.somda.sdc.dpws.client.DiscoveredDevice;

class TestDiscoveredDeviceAdapter {
    @Test
    void testSerializeAndDeserialize() {
        var gson = new GsonBuilder()
                .setFieldNamingPolicy(FieldNamingPolicy.LOWER_CASE_WITH_UNDERSCORES)
                .registerTypeAdapter(DiscoveredDevice.class, new DiscoveredDeviceAdapter())
                .create();

        var expectedDiscoveredDevice = new DiscoveredDevice(
                "fake_epr",
                List.of(
                        new QName("namespace 1", "local part 1", "prefix 1"),
                        new QName("namespace 2", "local part 2", "prefix 2")),
                List.of("scope 1", "scope 2"),
                List.of("xaddr 1", "xaddr 2"),
                3);

        var actualDiscoveredDevice = gson.fromJson(gson.toJson(expectedDiscoveredDevice), DiscoveredDevice.class);
        assertEquals(expectedDiscoveredDevice.getEprAddress(), actualDiscoveredDevice.getEprAddress());
        assertEquals(expectedDiscoveredDevice.getTypes(), actualDiscoveredDevice.getTypes());
        assertEquals(expectedDiscoveredDevice.getScopes(), actualDiscoveredDevice.getScopes());
        assertEquals(expectedDiscoveredDevice.getXAddrs(), actualDiscoveredDevice.getXAddrs());
        assertEquals(expectedDiscoveredDevice.getMetadataVersion(), actualDiscoveredDevice.getMetadataVersion());
    }
}
