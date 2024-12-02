Feature: Update device

  Scenario: Update Device
    Given the application is running
    And a request to update a device
    And valid authentication credentials are being included
    And the device exists
    And a new name is provided
    When the request is made to update a device
    Then the device is created
    And the user is told the request was successful

  Scenario: Update Device with gateway
    Given the application is running
    And a request to update a device
    And the device exists
    And valid authentication credentials are being included
    And a new name is provided
    And the device is assigned a gateway
    And a device with the gateway id exists
    When the request is made to update a device
    Then the device is updated
    And the user is told the request was successful

  Scenario: Update Device - device does not exist
    Given the application is running
    And a request to update a device
    And valid authentication credentials are being included
    And a new name is provided
    When the request is made to update a device
    And the user is told the device was not found

  Scenario: Credentials not provided
    Given the application is running
    And a request to update a device
    When the request is made to update a device
    Then the user is told the request was forbidden

  Scenario: Invalid credentials provided
    Given the application is running
    And a request to update a device
    And invalid authentication credentials are being included
    When the request is made to update a device
    Then the user is told the request was unauthorized
