Feature: Create Patient

  Scenario: Create Patient
    Given the application is running
    And a request to create a patient
    And valid authentication credentials are being included
    When the request is made to create a patient
    Then the user is told the request was successful
    And the patient is created
    And the new patient is returned
    And the create patient event is published

  Scenario: Create Patient without birthdate
    Given the application is running
    And a request to create a patient without birthdate
    And valid authentication credentials are being included
    When the request is made to create a patient
    Then the user is told the request was successful
    And the patient is created
    And the new patient is returned
    And the create patient without birthdate event is published

  Scenario: Create Patient - Id already in use
    Given the application is running
    And a request to create a patient
    And valid authentication credentials are being included
    And a patient with the same id already exists
    When the request is made to create a patient
    Then the user is told there payload is invalid

  Scenario: Create Patient - Primary identifier in use by other tenant
    Given the application is running
    And a request to create a patient
    And valid authentication credentials are being included
    And a patient with the same primary identifier already exists for other tenant
    When the request is made to create a patient
    Then the patient is not created
    And the user is told the primary identifier is already used

  Scenario Outline: Create Patient - Missing Values
    Given the application is running
    And a request to create a patient
    And valid authentication credentials are being included
    And the request includes no `<field_name>` field
    When the request is made to create a patient
    Then the patient is not created
    And the user is told there payload is invalid

    Examples:
      | field_name         |
      | primary_identifier |
      | active             |
      | given_name         |
      | family_name        |
      | gender             |
