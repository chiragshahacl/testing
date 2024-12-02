@API @PATIENT @SMOKE @SR-7.5.3
Feature: [API] Get Patient

  Background:
    Given the user credentials are valid
    And the tucana application is running
    And A request to create a new patient through Tucana's API
    When the request is made to create a patient
    Then the user is told the request to create was successful

  Scenario: Get patient by ID
    When the user wants to get the recently created user
    Then the user is told the get patient request was successful
    And the user verifies that all the Patient information is correct
    And The patient is removed to keep the application clean
