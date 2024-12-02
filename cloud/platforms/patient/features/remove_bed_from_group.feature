Feature: Remove Bed From Group

  Scenario: Remove Bed From Group (bed and group exist)
    Given the application is running
    And a request to remove bed from a group
    And valid authentication credentials are being included
    And the bed exists
    And the bed group exist
    And the bed is part of the group
    When the request to remove bed from a group is made
    And the user is told the request was successful with no content
    And the bed is removed from the group

  Scenario: Bed does not exist
    Given the application is running
    And a request to remove bed from a group
    And valid authentication credentials are being included
    And the bed group exist
    When the request to add bed to a group is made
    And the user is told the bed was not found

  Scenario: Group does not exist
    Given the application is running
    And a request to remove bed from a group
    And valid authentication credentials are being included
    And the bed exists
    When the request to remove bed from a group is made
    And the user is told the bed group name is not found

  Scenario: Bad credentials
    Given the application is running
    And a request to remove bed from a group
    And invalid authentication credentials are being included
    When the request to remove bed from a group is made
    Then the user is told the request was unauthorized
