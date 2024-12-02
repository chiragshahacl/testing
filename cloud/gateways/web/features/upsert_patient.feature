Feature: Upsert a Patient

  Scenario: Upsert a non-existing patient (happy path)
    Given the application is running
    And a request to upsert a patient
    And the patient to be upserted does not exist
    When the request is made to upsert a patient
    Then the user is told the request was successful
    And the user is told the patient was created

  Scenario: Upsert an existing patient (happy path)
    Given the application is running
    And a request to upsert a patient
    And the patient to be upserted exists
    When the request is made to upsert a patient
    Then the user is told the request was successful
    And the user is told the patient was updated

  Scenario: Upsert an existing patient with invalid payload
    Given the application is running
    And a request to upsert a patient is invalid
    And the patient to be upserted exists
    When the request is made to upsert a patient
    Then the user is told the request was invalid
