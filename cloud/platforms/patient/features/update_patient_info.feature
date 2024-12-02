Feature: Update patient

  Scenario: Update Patient
    Given the application is running
    And a request to update a patient
    And valid authentication credentials are being included
    And the patient already exists
    And a new patient_identifier is provided
    And a new active status is provided
    And a new given_name is provided
    And a new family_name is provided
    And a new gender is provided
    And a new birthdate is provided
    When the request is made to update a patient
    Then the patient is updated
    And the user is told the request was successful
    And the updated patient is returned
    And the update patient event is published

  Scenario: Update Patient - Patient does not exist
    Given the application is running
    And a request to update a patient
    And valid authentication credentials are being included
    And a new patient_identifier is provided
    And a new active status is provided
    And a new given_name is provided
    And a new family_name is provided
    And a new gender is provided
    And a new birthdate is provided
    When the request is made to update a patient
    Then the user is told the patient was not found

  Scenario: Credentials not provided
    Given the application is running
    And a request to update a patient
    When the request is made to update a patient
    Then the user is told the request was forbidden

  Scenario: Invalid credentials provided
    Given the application is running
    And a request to update a patient
    And invalid authentication credentials are being included
    When the request is made to update a patient
    Then the user is told the request was unauthorized
