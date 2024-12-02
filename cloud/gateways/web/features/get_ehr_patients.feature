Feature: Get EHR Patients

  Scenario: Get EHR Patients by patient identifier
    Given the application is running
    And a request to get EHR patients with the following parameters
      """
      patientIdentifier: 123
      """
    And the request includes valid authentication credentials
    And there are patients in the EHR
    When the request to get EHR patient is made
    Then the user is told the request was successful
    And the patients are in the response

  Scenario: Get EHR Patients by given and family name
    Given the application is running
    And a request to get EHR patients with the following parameters
      """
      givenName: John
      familyName: Doe
      """
    And the request includes valid authentication credentials
    And there are patients in the EHR
    When the request to get EHR patient is made
    Then the user is told the request was successful
    And the patients are in the response

  Scenario: Get EHR Patients by patient identifier and date of birth
    Given the application is running
    And a request to get EHR patients with the following parameters
      """
      patientIdentifier: 123
      birthDate: "2020-01-01"
      """
    And the request includes valid authentication credentials
    And there are patients in the EHR
    When the request to get EHR patient is made
    Then the user is told the request was successful
    And the patients are in the response

  Scenario: Get EHR Patients by given name, family name and date of birth
    Given the application is running
    And a request to get EHR patients with the following parameters
      """
      givenName: John
      familyName: Doe
      birthDate: "2020-01-01"
      """
    And the request includes valid authentication credentials
    And there are patients in the EHR
    When the request to get EHR patient is made
    Then the user is told the request was successful
    And the patients are in the response

  Scenario: Get EHR Patients by given name, family name and date of birth
    Given the application is running
    And a request to get EHR patients with the following parameters
      """
      givenName: John
      familyName: Doe
      birthDate: "2020-01-01"
      """
    And the request includes valid authentication credentials
    And there are patients in the EHR
    And some EHR patients are being monitored
    When the request to get EHR patient is made
    Then the user is told the request was successful
    And the monitored patients are not in the response

  Scenario: Get EHR Patients  - Missing values
    Given the application is running
    And a request to get EHR patients with the following parameters
      """
      """
    And the request includes valid authentication credentials
    And there are patients in the EHR
    When the request to get EHR patient is made
    Then the user is told their payload is invalid

  Scenario: Get EHR Patients  - Missing patientIdentifier or given and family name
    Given the application is running
    And a request to get EHR patients with the following parameters
      """
      birthDate: "2020-01-01"
      """
    And the request includes valid authentication credentials
    And there are patients in the EHR
    When the request to get EHR patient is made
    Then the user is told their payload is invalid
