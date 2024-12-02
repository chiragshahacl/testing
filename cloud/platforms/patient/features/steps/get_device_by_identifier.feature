Feature: Get Device by Identifier

  Scenario: Device exists
    Given the application is running
    And a valid request to get a device by identifier
    And valid authentication credentials are being included
    And the device exists
    When the request is made to get a device by identifier
    Then the device is fetched
    And the user is told the request was successful

  Scenario: Patient monitor exists
    Given the application is running
    And a valid request to get a device by identifier
    And valid authentication credentials are being included
    And the patient monitor exists
    When the request is made to get a device by identifier
    Then the device is fetched
    And the user is told the request was successful

  Scenario: Device exists - Case Insensitive identifier
    Given the application is running
    And a valid request to get a device by identifier
    And valid authentication credentials are being included
    And the device identifier id was provided in uppercase
    And the device exists
    When the request is made to get a device by identifier
    Then the device is fetched
    And the user is told the request was successful

  Scenario: Device does not exist
    Given the application is running
    And a valid request to get a device by identifier
    And valid authentication credentials are being included
    When the request is made to get a device by identifier
    Then the user is told the device was not found

  Scenario: Credentials not provided
    Given the application is running
    And a valid request to get a device by identifier
    When the request is made to get a device by identifier
    Then the user is told the request was forbidden

  Scenario: Invalid credentials provided
    Given the application is running
    And a valid request to get a device by identifier
    And invalid authentication credentials are being included
    When the request is made to get a device by identifier
    Then the user is told the request was unauthorized
