Feature: Batch assign locations to devices

  Scenario: Assign location to one device
    Given the application is running
    And a request to assign a location to devices
    And the device exists
    And the bed exists
    And valid authentication credentials are being included
    When the request is made to assign locations
    Then the user is told the request was successful
    And the device location is assigned correctly

  Scenario: Assign locations to multiple devices
    Given the application is running
    And a request to assign a location to multiple devices
    And the beds exist
    And the devices exist
    And valid authentication credentials are being included
    When the request is made to assign locations
    Then the user is told the request was successful
    And the devices locations are assigned correctly

  Scenario: A device does not exist
    Given the application is running
    And a request to assign a location to devices
    And valid authentication credentials are being included
    When the request is made to assign locations
    Then the user is told there payload is invalid

  Scenario: Invalid payload
    Given the application is running
    And a request to assign a location to devices
    And the device exists
    And valid authentication credentials are being included
    But the request payload is wrong
    When the request is made to assign locations
    Then the user is told there payload is invalid

  Scenario: Location already assigned
    Given the application is running
    And a request to assign a location to devices
    And the device exists
    And the bed exists
    And valid authentication credentials are being included
    But the location is already assigned to other device
    When the request is made to assign locations
    Then the user is told there payload is invalid
    And the device location is not assigned

  Scenario: Credentials not provided
    Given the application is running
    And a request to assign a location to devices
    When the request is made to assign locations
    Then the user is told the request was forbidden

  Scenario: Invalid credentials provided
    Given the application is running
    And a request to assign a location to devices
    And invalid authentication credentials are being included
    When the request is made to assign locations
    Then the user is told the request was unauthorized
