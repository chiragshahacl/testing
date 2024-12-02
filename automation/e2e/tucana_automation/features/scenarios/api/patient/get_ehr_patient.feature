@API @PATIENT @SMOKE @SR-7.5.3
Feature: [API] Get EHR Patient

  Background:
    Given the user credentials are valid
    And the tucana application is running
    And The patient from EHR exists with the following data
    """
    patient:
      primary_patient_id: "001"
      dob: "2012-01-01"
      family_name: Smith
      given_name: Robert
      gender: M
    """

  Scenario: Get EHR patient by patientIdentifier
    When the user wants to get the EHR patient by "patientIdentifier"
    Then the user is told the get patient request was successful
    And the user verifies that the EHR Patient information is correct

  Scenario: Get EHR patient by givenName
    When the user wants to get the EHR patient by "givenName"
    Then the user is told the get patient request was successful
    And the user verifies that the EHR Patient information is correct

  Scenario: Get EHR patient by familyName
    When the user wants to get the EHR patient by "familyName"
    Then the user is told the get patient request was successful
    And the user verifies that the EHR Patient information is correct

  Scenario: Get EHR patient by birthDate
    When the user wants to get the EHR patient by "birthDate"
    Then the user is told the get patient request was successful
    And the user verifies that the EHR Patient information is correct