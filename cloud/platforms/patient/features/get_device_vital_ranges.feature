Feature: Get Device Vital Ranges

  Scenario: Get Device Vital Ranges
    Given the application is running
    And a request to get a device's vital ranges
    And the device exists with `5` vital ranges
    And valid authentication credentials are being included
    When the request is made to get a device's vital ranges
    Then the user is told the request was successful
    And the device vital ranges are returned

  Scenario: Get Device Vital Ranges with some out of scope
    Given the application is running
    And a request to get a device's vital ranges
    And the device exists with `5` vital ranges, some out of scope
    And valid authentication credentials are being included
    When the request is made to get a device's vital ranges
    Then the user is told the request was successful
    And the device vital ranges are returned

  Scenario: Credentials not provided
    Given the application is running
    And a request to get a device's vital ranges
    When the request is made to get a device's vital ranges
    Then the user is told the request was forbidden

  Scenario: Invalid credentials provided
    Given the application is running
    And a request to get a device's vital ranges
    And invalid authentication credentials are being included
    When the request is made to get a device's vital ranges
    Then the user is told the request was unauthorized
