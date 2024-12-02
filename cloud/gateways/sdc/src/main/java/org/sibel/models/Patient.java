package org.sibel.models;

public record Patient(String givenName, String familyName, Gender gender, String birthDate) {}
