package org.sibel.apis;

import com.google.gson.Gson;
import com.google.inject.Inject;
import java.net.http.HttpRequest;
import java.util.Collection;
import java.util.List;
import java.util.stream.Stream;
import org.apache.http.NameValuePair;
import org.apache.http.message.BasicNameValuePair;
import org.sibel.apis.auth.JWTAuth;
import org.sibel.config.Settings;
import org.sibel.exceptions.ApiRequestException;
import org.sibel.models.api.EhrPatient;
import org.sibel.models.api.EhrSearchCriteria;
import org.sibel.models.api.EhrSearchPatientResponse;

public class EhrApiImpl extends BaseApi implements EhrApi {
    private final Settings settings;
    private final JWTAuth auth;

    @Inject
    protected EhrApiImpl(Gson gson, Settings settings, JWTAuth auth) {
        super(gson);
        this.settings = settings;
        this.auth = auth;
    }

    @Override
    public Collection<EhrPatient> searchPatients(EhrSearchCriteria criteria) throws ApiRequestException {
        var queryParams = Stream.of(
                        new BasicNameValuePair("patientIdentifier", criteria.patientIdentifier()),
                        new BasicNameValuePair("givenName", criteria.givenName()),
                        new BasicNameValuePair("familyName", criteria.familyName()),
                        new BasicNameValuePair("birthDate", criteria.birthDate()))
                .filter(param -> param.getValue() != null && !param.getValue().isBlank())
                .map(param -> (NameValuePair) param)
                .toList();
        var uri = getEndpointUri(settings.EHR_SERVICE_URL(), List.of("query", "patient"), queryParams);
        var request = HttpRequest.newBuilder(uri)
                .header("Authorization", "Bearer %s".formatted(auth.getJwtToken()))
                .GET()
                .build();
        return sendRequest(request, EhrSearchPatientResponse.class).resources();
    }
}
