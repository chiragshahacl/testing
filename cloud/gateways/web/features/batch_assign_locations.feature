Feature: Batch Assign Locations to Devices
  """
  A location is a bed
  """

  Scenario: Assign Location to one Device
    Given the application is running
    And a request to batch assign location to a device
    And with a valid auth credentials
    And the device can be assigned
    When the request is made to assign some locations
    Then the user is told the request was successful with no content

  Scenario: Assign multiple locations to devices
    Given the application is running
    And a request to batch assign multiple locations to devices
    And with a valid auth credentials
    And the device can be assigned
    When the request is made to assign some locations
    Then the user is told the request was successful with no content

  Scenario: Unassign bed
    Given the application is running
    And a request to batch assign multiple locations to devices
    And one of the devices is being unassigned from a bed
    And with a valid auth credentials
    And the device can be assigned
    And the device can be unassigned
    When the request is made to assign some locations
    Then the user is told the request was successful with no content

  Scenario: Invalid auth
    Given the application is running
    And a request to batch assign location to a device
    And with invalid auth credentials
    And the device can be assigned
    When the request is made to assign some locations
    Then the user is told the request was unauthorized

  Scenario: Credentials not provided
    Given the application is running
    And a request to batch assign location to a device
    When the request is made to assign some locations
    Then the user is told the request was forbidden
