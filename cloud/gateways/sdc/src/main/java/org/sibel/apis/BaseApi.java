package org.sibel.apis;

import com.google.gson.Gson;
import com.google.gson.JsonParseException;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.List;
import org.apache.http.NameValuePair;
import org.apache.http.client.utils.URIBuilder;
import org.sibel.exceptions.ApiRequestException;

public abstract class BaseApi {
    protected final Gson gson;

    protected BaseApi(Gson gson) {
        this.gson = gson;
    }

    protected static URI getEndpointUri(String rootUrl, List<String> pathSegments, List<NameValuePair> queryParams)
            throws ApiRequestException {
        URI uri;
        try {
            var builder = new URIBuilder(rootUrl).setPathSegments(pathSegments);
            if (queryParams != null) {
                builder.setParameters(queryParams);
            }
            uri = builder.build();
        } catch (URISyntaxException e) {
            throw new ApiRequestException("Error constructing patient URI", e);
        }
        return uri;
    }

    protected <T> T sendRequest(HttpRequest request, Class<T> responseType) throws ApiRequestException {
        HttpResponse<String> response;
        try {
            var httpClient =
                    HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1).build();
            response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        } catch (IOException | InterruptedException e) {
            throw new ApiRequestException("Error executing request", e);
        }
        if (response.statusCode() != 200) {
            throw new ApiRequestException("Error response status %d received.".formatted(response.statusCode()));
        }
        return parseResponse(response, responseType);
    }

    private <T> T parseResponse(HttpResponse<String> response, Class<T> responseType) throws ApiRequestException {
        var data = response.body();
        try {
            return gson.fromJson(data, responseType);
        } catch (JsonParseException e) {
            throw new ApiRequestException("Error parsing patient response.", e);
        }
    }
}
