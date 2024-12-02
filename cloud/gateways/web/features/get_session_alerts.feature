Feature: Get Session Alerts

  Scenario: Happy path
    Given the application is running
    And a patient exists
    And the patient's device has technical alerts
    And the patient has alerts physiological alerts
    And a request is set to get a patient physiological alerts
    And a request to get session alerts
    And with a valid auth credentials
    When the request to get session alerts is made
    Then the user is told the request was successful
    And the expected response is returned
