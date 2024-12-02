package org.sibel.models.api;

public record ApiPatient(
        String id,
        String primaryIdentifier,
        String givenName,
        String familyName,
        String birthDate,
        String gender,
        boolean active) {}
