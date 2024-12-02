Feature: Delete existing device

  Scenario: Delete Device
    Given the application is running
    And a request is made to delete a device
    And valid authentication credentials are being included
    And the device exists
    When the request is made to delete the device
    Then the device no longer exists
    And the user is told the request was successful
