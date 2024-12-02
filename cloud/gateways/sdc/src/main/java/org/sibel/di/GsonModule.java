package org.sibel.di;

import com.google.gson.FieldNamingPolicy;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.inject.AbstractModule;
import com.google.inject.Provides;
import java.time.Instant;
import java.util.Optional;
import org.sibel.constants.SensorType;
import org.sibel.models.CommandEventBrokerMessage;
import org.sibel.models.Gender;
import org.sibel.models.api.EhrPatient;
import org.sibel.models.jsonAdapters.*;
import org.sibel.models.scoParams.SetPatientContextParams;
import org.somda.sdc.biceps.model.participant.Sex;
import org.somda.sdc.dpws.client.DiscoveredDevice;

public class GsonModule extends AbstractModule {
    private final boolean prettyPrint;

    public GsonModule() {
        this(false);
    }

    public GsonModule(boolean prettyPrint) {
        this.prettyPrint = prettyPrint;
    }

    @Provides
    public Gson getGson() {
        var gsonBuilder = new GsonBuilder()
                .setFieldNamingPolicy(FieldNamingPolicy.LOWER_CASE_WITH_UNDERSCORES)
                .registerTypeAdapter(DiscoveredDevice.class, new DiscoveredDeviceAdapter())
                .registerTypeHierarchyAdapter(Optional.class, new OptionalTypeAdapter<>())
                .registerTypeAdapter(Instant.class, new InstantAdapter())
                .registerTypeAdapter(CommandEventBrokerMessage.class, new CommandEventBrokerMessageAdapter())
                .registerTypeAdapter(SetPatientContextParams.class, new SetPatientContextParamsAdapter())
                .registerTypeAdapter(Sex.class, new SexAdapter())
                .registerTypeAdapter(EhrPatient.class, new EhrPatientAdapter())
                .registerTypeAdapter(SensorType.class, new SensorTypeAdapter())
                .registerTypeAdapter(Gender.class, new GenderAdapter());

        if (prettyPrint) {
            gsonBuilder.setPrettyPrinting();
        }

        return gsonBuilder.create();
    }
}
