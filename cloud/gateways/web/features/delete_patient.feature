Feature: Delete Patient

  Scenario: Delete Patient
    Given the application is running
    And a request to delete a patient
    And with a valid auth credentials
    And the patient exists
    When the request is made to delete a patient
    Then the user is told the request was successful with no content

  Scenario: Delete patient that doesn't exist
    Given the application is running
    And a request to delete a patient
    And with a valid auth credentials
    And the patient doesnt exist
    When the request is made to delete a patient
    Then the user is told their payload is invalid

  Scenario: Delete patient, invalid auth
    Given the application is running
    And a request to delete a patient
    And with invalid auth credentials
    And the patient doesnt exist
    When the request is made to delete a patient
    Then the user is told the request was unauthorized
