package org.sibel.models;

import java.util.Arrays;
import java.util.List;
import org.sibel.constants.FhirGenders;
import org.sibel.constants.Hl7Genders;
import org.somda.sdc.biceps.model.participant.Sex;

public enum Gender {
    MALE(List.of(Hl7Genders.MALE), FhirGenders.MALE, Sex.M),
    FEMALE(List.of(Hl7Genders.FEMALE), FhirGenders.FEMALE, Sex.F),
    OTHER(List.of(Hl7Genders.OTHER, Hl7Genders.AMBIGUOUS, Hl7Genders.NON_BINARY), FhirGenders.OTHER, Sex.UNSPEC),
    UNKNOWN(List.of(Hl7Genders.UNKNOWN, Hl7Genders.NOT_APPLICABLE), FhirGenders.UNKNOWN, Sex.UNKN);

    private final List<String> fhirGenderValues;
    private final String fhirGenderConcept;
    private final Sex mdibSex;

    Gender(List<String> fhirGenderValues, String fhirGenderConcept, Sex mdibSex) {
        this.fhirGenderValues = fhirGenderValues;
        this.fhirGenderConcept = fhirGenderConcept;
        this.mdibSex = mdibSex;
    }

    public List<String> getFhirGenderValues() {
        return fhirGenderValues;
    }

    public String getFhirGenderConcept() {
        return fhirGenderConcept;
    }

    public Sex getMdibSex() {
        return mdibSex;
    }

    public static Gender fromFhirGenderValue(String fhirGenderValue) {
        return Arrays.stream(values())
                .filter(gender -> gender.fhirGenderValues.contains(fhirGenderValue))
                .findFirst()
                .orElse(UNKNOWN);
    }

    public static Gender fromFhirGenderConcept(String fhirGenderConcept) {
        return Arrays.stream(values())
                .filter(gender -> gender.fhirGenderConcept.equals(fhirGenderConcept))
                .findFirst()
                .orElse(UNKNOWN);
    }

    public static Gender fromMdibSex(Sex mdibSex) {
        return Arrays.stream(values())
                .filter(gender -> gender.mdibSex.equals(mdibSex))
                .findFirst()
                .orElse(UNKNOWN);
    }
}
