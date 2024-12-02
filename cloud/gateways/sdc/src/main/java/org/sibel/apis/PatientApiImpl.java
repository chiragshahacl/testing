package org.sibel.apis;

import com.google.gson.Gson;
import com.google.inject.Inject;
import java.net.http.HttpRequest;
import java.util.List;
import org.sibel.apis.auth.JWTAuth;
import org.sibel.config.Settings;
import org.sibel.exceptions.ApiRequestException;
import org.sibel.models.api.ApiPatient;

public class PatientApiImpl extends BaseApi implements PatientApi {
    private final JWTAuth auth;
    private final Settings settings;

    @Inject
    public PatientApiImpl(Gson gson, Settings settings, JWTAuth auth) {
        super(gson);
        this.auth = auth;
        this.settings = settings;
    }

    @Override
    public ApiPatient getPatient(String primaryIdentifier) throws ApiRequestException {
        var uri = getEndpointUri(
                settings.PATIENT_SERVICE_URL(), List.of("patient", "identifier", primaryIdentifier), null);
        var request = HttpRequest.newBuilder(uri)
                .header("Authorization", "Bearer %s".formatted(auth.getJwtToken()))
                .GET()
                .build();
        return sendRequest(request, ApiPatient.class);
    }
}
