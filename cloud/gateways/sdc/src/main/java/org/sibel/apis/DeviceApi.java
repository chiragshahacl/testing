package org.sibel.apis;

import org.sibel.exceptions.ApiRequestException;
import org.sibel.models.api.ApiPatientMonitorEncounter;

public interface DeviceApi {
    ApiPatientMonitorEncounter getDeviceEncounter(String primaryIdentifier) throws ApiRequestException;
}
