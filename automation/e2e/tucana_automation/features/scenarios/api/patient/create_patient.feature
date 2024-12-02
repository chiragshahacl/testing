@API @PATIENT @SMOKE @SR-7.5.3
Feature: [API] Create Patient

  Background:
    Given the user credentials are valid

  Scenario: Create a new Patient
    Given the Tucana application is running
    And A request to create a new patient through Tucana's API
    And authentication credentials are being included
    When the request is made to create a patient
    Then the user is told the request to create was successful
    And the patient is created
    And The patient is removed to keep the application clean

  Scenario: Create a new Patient - Invalid payload
    Given the Tucana application is running
    And a request to create a patient with invalid gender "human" in payload
    And authentication credentials are being included
    When the request is made to create a patient
    Then the user is told their payload is invalid

  Scenario: Create a new Patient - Authentication not provided
    Given the Tucana application is running
    And A request to create a new patient through Tucana's API
    And authentication credentials are not being included
    When the request is made to create a patient
    Then the user is told the request was forbidden

  Scenario: Create a new Patient - Invalid credentials
    Given the Tucana application is running
    And A request to create a new patient through Tucana's API
    And authentication credentials are being included
    And the credentials are not valid
    When the request is made to create a patient
    Then the user is told the request was unauthorized