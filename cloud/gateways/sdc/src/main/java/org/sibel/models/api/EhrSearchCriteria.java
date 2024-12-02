package org.sibel.models.api;

import java.util.Objects;
import org.sibel.dataProcessors.PatientContextChangeProcessor;
import org.sibel.models.payloads.internal.PatientPayload;
import org.sibel.utils.StringUtils;

public record EhrSearchCriteria(String patientIdentifier, String givenName, String familyName, String birthDate) {
    public static EhrSearchCriteria fromPatientPayload(PatientPayload payload) {
        return new EhrSearchCriteria(
                StringUtils.trim(payload.getPrimaryIdentifier()),
                parseEmptyValues(StringUtils.trim(payload.getGivenName())),
                parseEmptyValues(StringUtils.trim(payload.getFamilyName())),
                parseDob(StringUtils.trim(payload.getBirthDate())));
    }

    private static String parseDob(String patientPayloadDob) {
        return patientPayloadDob != null ? patientPayloadDob.replace("-", "") : null;
    }

    // TODO: This should not be necessary if we send null as it should be
    private static String parseEmptyValues(String payload) {
        return Objects.equals(payload, PatientContextChangeProcessor.DEFAULT_EMPTY_PATIENT_DATA_VALUE) ? null : payload;
    }
}
