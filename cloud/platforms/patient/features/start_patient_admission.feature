Feature: Start Patient Admission

  Scenario: Start Patient Admission successfully
    Given the application is running
    And a request to plan a patient admission
    And valid authentication credentials are being included
    When the request is made to plan a patient admission
    Then the user is told the request was successful
    And the planned encounter is created
    And the new planned encounter is returned
    And the patient encounter planned event is published

  Scenario: Start Patient Admission with an existing encounter for the same patient and device
    Given the application is running
    And a request to plan a patient admission
    And valid authentication credentials are being included
    But an encounter for the patient and device already exists
    When the request is made to plan a patient admission
    Then the user is told the request was successful
    And the planned encounter is created
    And the new planned encounter is returned
    And the patient encounter planned event is published

  Scenario: Start Patient Admission with an existing encounter for the same patient
    Given the application is running
    And a request to plan a patient admission
    And valid authentication credentials are being included
    But an encounter for the patient already exists
    When the request is made to plan a patient admission
    Then the user is told the request was successful
    And the planned encounter is created
    And the new planned encounter is returned
    And the patient encounter planned event is published

  Scenario: Start Patient Admission with an existing encounter for the same device
    Given the application is running
    And a request to plan a patient admission
    And valid authentication credentials are being included
    But an encounter for the device already exists
    When the request is made to plan a patient admission
    Then the user is told the request was successful
    And the planned encounter is created
    And the new planned encounter is returned
    And the patient encounter planned event is published

  Scenario: Start Patient Admission with an existing encounter in progress
    Given the application is running
    And a request to plan a patient admission
    And valid authentication credentials are being included
    But an encounter for the device already exists with status `in-progress`
    When the request is made to plan a patient admission
    Then the user is told there payload is invalid
    And the planned encounter is not created

  Scenario: Bed does not exist for the Patient Admission
    Given the application is running
    And a request to plan a patient admission
    And valid authentication credentials are being included
    But the bed id is incorrect
    When the request is made to plan a patient admission
    Then the user is told there payload is invalid
    And the planned encounter is not created

  Scenario: Patient does not exist for the Patient Admission
    Given the application is running
    And a request to plan a patient admission
    And valid authentication credentials are being included
    But the patient id is incorrect
    When the request is made to plan a patient admission
    Then the user is told there payload is invalid
    And the planned encounter is not created
