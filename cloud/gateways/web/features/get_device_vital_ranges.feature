Feature: Get Device Vital Ranges

  Scenario: Get Device Vital Ranges (happy)
    Given the application is running
    And a request to get vital ranges for a certain device
    And the device has several ranges in existence
    And with a valid auth credentials
    When the request is made to get vital ranges
    Then the user is told the request was successful
    And the vital ranges are returned

  Scenario: invalid auth
    Given the application is running
    And beds are found
    And a request to get vital ranges for a certain device
    But with invalid auth credentials
    When the request is made to get vital ranges
    Then the user is told the request was unauthorized

  Scenario: Credentials not provided
    Given the application is running
    And beds are found
    And a request to get vital ranges for a certain device
    When the request is made to get vital ranges
    Then the user is told the request was forbidden
