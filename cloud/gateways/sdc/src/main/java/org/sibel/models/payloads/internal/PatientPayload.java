package org.sibel.models.payloads.internal;

import static org.sibel.mdib.MdibUtils.getFhirGenderFromSex;
import static org.sibel.mdib.MdibUtils.getSexFromFhirGender;

import com.google.common.base.MoreObjects;
import java.util.*;
import org.sibel.models.api.ApiPatient;
import org.sibel.models.payloads.AlertPayload;
import org.somda.sdc.biceps.model.participant.ContextAssociation;
import org.somda.sdc.biceps.model.participant.Sex;

public class PatientPayload {
    private static final List<String> EMPTY_PATIENT_IDS = List.of("0", "Unknown");

    private String primary_identifier;
    private String given_name;
    private String family_name;
    private String gender;
    private String birth_date;
    private List<AlertPayload> alerts = List.of();

    private transient ContextAssociation association;
    private transient Set<String> validators;

    public PatientPayload(
            String primaryIdentifier,
            String givenName,
            String familyName,
            String birthDate,
            Sex gender,
            ContextAssociation association,
            Set<String> validators) {
        this(
                primaryIdentifier,
                givenName,
                familyName,
                birthDate,
                getFhirGenderFromSex(gender),
                association,
                validators);
    }

    public PatientPayload(
            String primaryIdentifier,
            String givenName,
            String familyName,
            String birthDate,
            String gender,
            ContextAssociation association,
            Set<String> validators) {
        this.primary_identifier = primaryIdentifier;
        this.given_name = givenName;
        this.family_name = familyName;
        this.birth_date = birthDate;
        this.gender = gender;
        this.association = association;
        this.validators = validators;
    }

    public static PatientPayload createEmpty(ContextAssociation association) {
        return new PatientPayload("Unknown", null, null, null, (String) null, association, null);
    }

    public static PatientPayload fromApiPatient(ApiPatient patient, Set<String> validators) {
        return new PatientPayload(
                patient.primaryIdentifier(),
                patient.givenName(),
                patient.familyName(),
                patient.birthDate(),
                patient.gender(),
                ContextAssociation.ASSOC,
                validators);
    }

    public String getPrimaryIdentifier() {
        return primary_identifier;
    }

    public String getGivenName() {
        return given_name;
    }

    public String getFamilyName() {
        return family_name;
    }

    public String getBirthDate() {
        return birth_date;
    }

    public Sex getGender() {
        return getSexFromFhirGender(gender);
    }

    public String getGenderText() {
        return gender;
    }

    public List<AlertPayload> getAlerts() {
        return alerts;
    }

    public void setAlerts(List<AlertPayload> alerts) {
        this.alerts = alerts;
    }

    public ContextAssociation getAssociation() {
        return association;
    }

    public boolean hasValidators(String... validators) {
        return this.validators != null && this.validators.containsAll(Arrays.asList(validators));
    }

    public List<String> getValidators() {
        return validators != null ? validators.stream().toList() : null;
    }

    public boolean isEmpty() {
        return primary_identifier == null
                || primary_identifier.isBlank()
                || EMPTY_PATIENT_IDS.stream().anyMatch(primary_identifier::equals);
    }

    @Override
    public boolean equals(Object other) {
        return this == other
                || other instanceof PatientPayload
                        && Objects.equals(this.primary_identifier, ((PatientPayload) other).primary_identifier)
                        && Objects.equals(this.given_name, ((PatientPayload) other).given_name)
                        && Objects.equals(this.family_name, ((PatientPayload) other).family_name)
                        && Objects.equals(this.gender, ((PatientPayload) other).gender)
                        && Objects.equals(this.birth_date, ((PatientPayload) other).birth_date);
    }

    @Override
    public int hashCode() {
        return Objects.hash(primary_identifier, given_name, family_name, gender, birth_date, alerts);
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("primary_identifier", primary_identifier)
                .add("given_name", "*******")
                .add("family_name", "*******")
                .add("gender", gender)
                .add("birth_date", "*******")
                .add("alerts", alerts)
                .toString();
    }
}
