package org.sibel.models.scoParams;

import static org.sibel.mdib.MdibUtils.getSexFromFhirGender;
import static org.sibel.mdib.MdibUtils.getSexFromHl7Gender;

import java.util.Collection;
import java.util.List;
import org.sibel.models.PatientEncounterPlannedMessage;
import org.sibel.models.api.ApiPatient;
import org.sibel.models.api.EhrPatient;
import org.sibel.models.payloads.internal.PatientPayload;
import org.sibel.utils.StringUtils;
import org.somda.sdc.biceps.model.participant.ContextAssociation;
import org.somda.sdc.biceps.model.participant.Sex;

public record SetPatientContextParams(List<Patient> patients) {
    public record Patient(
            String primaryIdentifier,
            String givenName,
            String familyName,
            Sex gender,
            String birthDate,
            ContextAssociation association) {
        public static Patient fromEhrPatient(EhrPatient ehrPatient, ContextAssociation association) {
            return new Patient(
                    StringUtils.trim(
                            ehrPatient.patientIdentifiers().stream().findFirst().orElse(null)),
                    StringUtils.trim(ehrPatient.givenName()),
                    StringUtils.trim(ehrPatient.familyName()),
                    getSexFromHl7Gender(ehrPatient.gender()),
                    parseDob(ehrPatient.birthDate()),
                    association);
        }
    }

    public static SetPatientContextParams fromPatientPayload(PatientPayload payload) {
        return new SetPatientContextParams(List.of(new Patient(
                payload.getPrimaryIdentifier(),
                payload.getGivenName(),
                payload.getFamilyName(),
                payload.getGender(),
                payload.getBirthDate(),
                payload.getAssociation())));
    }

    public static SetPatientContextParams fromPatientPayload(PatientPayload payload, ContextAssociation association) {
        return new SetPatientContextParams(List.of(new Patient(
                payload.getPrimaryIdentifier(),
                payload.getGivenName(),
                payload.getFamilyName(),
                payload.getGender(),
                payload.getBirthDate(),
                association)));
    }

    public static SetPatientContextParams fromApiPatient(ApiPatient patient) {
        return new SetPatientContextParams(List.of(new Patient(
                patient.primaryIdentifier(),
                patient.givenName(),
                patient.familyName(),
                getSexFromFhirGender(patient.gender()),
                patient.birthDate(),
                ContextAssociation.ASSOC)));
    }

    public static SetPatientContextParams fromEhrPatients(
            Collection<EhrPatient> ehrPatients, ContextAssociation association) {
        return new SetPatientContextParams(ehrPatients.stream()
                .map(ehrPatient -> Patient.fromEhrPatient(ehrPatient, association))
                .toList());
    }

    public static SetPatientContextParams fromPatientEncounterPlannedMessage(PatientEncounterPlannedMessage message) {
        var patient = message.eventState().patient();
        return new SetPatientContextParams(List.of(new Patient(
                patient.primaryIdentifier(),
                patient.givenName(),
                patient.familyName(),
                getSexFromFhirGender(patient.gender()),
                patient.birthDate(),
                ContextAssociation.ASSOC)));
    }

    private static String parseDob(String ehrDob) {
        String dob = null;
        if (ehrDob != null && !ehrDob.isBlank()) {
            var year = ehrDob.substring(0, 4);
            var month = ehrDob.substring(4, 6);
            var day = ehrDob.substring(6, 8);
            dob = "%s-%s-%s".formatted(year, month, day);
        }
        return dob;
    }
}
