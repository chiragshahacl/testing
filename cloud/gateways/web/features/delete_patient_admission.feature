Feature: Delete Patient Admission

  Scenario: Delete Patient Admission
    Given the application is running
    And a request to delete a patient admission
    And with a valid auth credentials
    And the patient admission exists
    When the request is made to delete a patient admission
    Then the user is told the request was successful with no content

  Scenario: Delete patient admission that doesn't exist
    Given the application is running
    And a request to delete a patient admission
    And with a valid auth credentials
    And the patient admission doesnt exist
    When the request is made to delete a patient admission
    Then the user is told their payload is invalid

  Scenario: Invalid Auth
    Given the application is running
    And a request to delete a patient admission
    And with invalid auth credentials
    And the patient admission doesnt exist
    When the request is made to delete a patient admission
    Then the user is told the request was unauthorized

  Scenario: Credentials not provided
    Given the application is running
    And a request to delete a patient admission
    And the patient admission doesnt exist
    When the request is made to delete a patient admission
    Then the user is told the request was forbidden
