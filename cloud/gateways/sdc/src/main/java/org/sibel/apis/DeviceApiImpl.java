package org.sibel.apis;

import com.google.gson.Gson;
import com.google.inject.Inject;
import java.net.http.HttpRequest;
import java.util.List;
import org.sibel.apis.auth.JWTAuth;
import org.sibel.config.Settings;
import org.sibel.exceptions.ApiRequestException;
import org.sibel.models.api.ApiPatientMonitorEncounter;
import org.sibel.models.api.GetPatientMonitorEncounterResponse;

public class DeviceApiImpl extends BaseApi implements DeviceApi {
    private final JWTAuth auth;
    private final Settings settings;

    @Inject
    public DeviceApiImpl(Gson gson, Settings settings, JWTAuth auth) {
        super(gson);
        this.auth = auth;
        this.settings = settings;
    }

    @Override
    public ApiPatientMonitorEncounter getDeviceEncounter(String primaryIdentifier) throws ApiRequestException {
        var uri =
                getEndpointUri(settings.PATIENT_SERVICE_URL(), List.of("device", primaryIdentifier, "admission"), null);
        var request = HttpRequest.newBuilder(uri)
                .header("Authorization", "Bearer %s".formatted(auth.getJwtToken()))
                .GET()
                .build();
        var response = sendRequest(request, GetPatientMonitorEncounterResponse.class);
        return response.resource();
    }
}
