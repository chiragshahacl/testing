Feature: Create device

  Scenario: Create Device
    Given the application is running
    And a request to create a device
    And valid authentication credentials are being included
    When the request is made to create a device
    Then the device is created
    And the user is told the request was successful
    And the created device also has default vital ranges

  Scenario: Create Device with gateway
    Given the application is running
    And a request to create a device
    And the device is assigned a gateway
    And a device with the gateway id exists
    And valid authentication credentials are being included
    When the request is made to create a device
    Then the device is created
    And the user is told the request was successful

  Scenario: Create Device - Id already in use
    Given the application is running
    And a request to create a device
    And valid authentication credentials are being included
    And a device with the same id already exists
    When the request is made to create a device
    Then the user is told there payload is invalid

  Scenario: Create Device - Primary Id already in use
    Given the application is running
    And a request to create a device
    And valid authentication credentials are being included
    And a device with the same primary identifier already exists
    When the request is made to create a device
    Then the user is told there payload is invalid

  Scenario Outline: Create Device - Missing Values
    Given the application is running
    And a request to create a device
    And valid authentication credentials are being included
    And the request includes no `<field_name>` field
    When the request is made to create a device
    Then the device is not created
    And the user is told there payload is invalid

    Examples:
      | field_name         |
      | id                 |
      | primary_identifier |
      | name               |

  Scenario: Credentials not provided
    Given the application is running
    And a request to create a device
    When the request is made to create a device
    Then the user is told the request was forbidden

  Scenario: Invalid credentials provided
    Given the application is running
    And a request to create a device
    And invalid authentication credentials are being included
    When the request is made to create a device
    Then the user is told the request was unauthorized
