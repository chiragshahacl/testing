Feature: Create a Patient

  Scenario: Create a patient (happy path)
    Given the application is running
    And a request to create a patient
    And the patient to be created does not exist
    When the request is made to create a patient
    Then the user is told the request was successful
    And the patient is created

  Scenario: Create a patient (without birthdate)
    Given the application is running
    And a request to create a patient without birthdate
    And the patient to be created does not exist
    When the request is made to create a patient
    Then the user is told the request was successful
    And the patient is created

  Scenario: Create an existing patient
    Given the application is running
    And a request to create a patient
    And the patient to be created exists
    When the request is made to create a patient
    Then the user is told the request was invalid
