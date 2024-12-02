package org.sibel.apis;

import java.util.Collection;
import org.sibel.exceptions.ApiRequestException;
import org.sibel.models.api.EhrPatient;
import org.sibel.models.api.EhrSearchCriteria;

public interface EhrApi {
    Collection<EhrPatient> searchPatients(EhrSearchCriteria criteria) throws ApiRequestException;
}
