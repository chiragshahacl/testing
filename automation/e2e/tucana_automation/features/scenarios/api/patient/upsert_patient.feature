@API @PATIENT @SMOKE @SR-7.5.3
Feature: [API] Upsert Patient

  Background:
    Given the user credentials are valid

  Scenario: Create a new Patient using upsert endpoint
    Given the Tucana application is running
    And A request to create a new patient through upsert endpoint
    And authentication credentials are being included
    When the request is made to create a patient through upsert endpoint
    Then the user is told the request was successful
    When the user wants to get the recently created user
    Then the user is told the get patient request was successful
    And the user verifies that all the Patient information is correct
    And The patient is removed to keep the application clean

  Scenario: Update a Patient using upsert endpoint
    Given the Tucana application is running
    And the patient exist
    And A request to update a patient through upsert endpoint
    And authentication credentials are being included
    When the request is made to update a patient through upsert endpoint
    Then the user is told the request to update was successful
    When the user wants to get the recently created user
    Then the user is told the get patient request was successful
    And the user verifies that all the Patient information is correct
    And The patient is removed to keep the application clean

  Scenario: Update a Patient - Authentication not provided
    Given the Tucana application is running
    And A request to create a new patient through upsert endpoint
    And authentication credentials are not being included
    When the request is made to create a patient through upsert endpoint
    Then the user is told the request was forbidden

  Scenario: Update a Patient - Invalid credentials
    Given the Tucana application is running
    And A request to create a new patient through upsert endpoint
    And authentication credentials are being included
    And the credentials are not valid
    When the request is made to create a patient through upsert endpoint
    Then the user is told the request was unauthorized