package org.sibel.models.api;

import java.util.Collection;

public record EhrPatient(
        Collection<String> patientIdentifiers, String givenName, String familyName, String birthDate, String gender) {}
