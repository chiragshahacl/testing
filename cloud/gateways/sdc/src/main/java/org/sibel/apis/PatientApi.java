package org.sibel.apis;

import org.sibel.exceptions.ApiRequestException;
import org.sibel.models.api.ApiPatient;

public interface PatientApi {
    ApiPatient getPatient(String primaryIdentifier) throws ApiRequestException;
}
