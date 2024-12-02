Feature: Batch unassign locations

  Scenario: Happy Path
    Given the application is running
    And a valid request to batch unassign location from devices
    And valid authentication credentials are being included
    And the beds exist
    And the devices in the request exist
    And some other devices with assigned location not in the request exist
    When the application receives the request to batch unassign location from devices
    Then the user is told the request was successful
    And the location is unassigned from the devices in the request
    And the unassigned events are published

  Scenario: Requested device does not exist
    Given the application is running
    And a valid request to batch unassign location from devices
    And valid authentication credentials are being included
    And the beds exist
    And one device in the request does not exist
    And some other devices with assigned location not in the request exist
    When the application receives the request to batch unassign location from devices
    Then the user is told there payload is invalid
    And no location is unassigned
    And the unassigned events are not published

  Scenario: Credentials not provided
    Given the application is running
    And a valid request to batch unassign location from devices
    When the application receives the request to batch unassign location from devices
    Then the user is told the request was forbidden

  Scenario: Invalid credentials provided
    Given the application is running
    And a valid request to batch unassign location from devices
    And invalid authentication credentials are being included
    When the application receives the request to batch unassign location from devices
    Then the user is told the request was unauthorized
