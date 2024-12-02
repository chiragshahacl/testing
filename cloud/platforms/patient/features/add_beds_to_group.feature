Feature: Add bed to group

  Scenario: Adds bed to the group
    Given the application is running
    And a request to add bed to a group
    And valid authentication credentials are being included
    And the bed exists
    And the bed group exist
    When the request to add bed to a group is made
    And the user is told the request was successful
    And the bed is assigned to the group

  Scenario: Group gets full with assignment
    Given the application is running
    And a request to add bed to a group
    And valid authentication credentials are being included
    And the bed exists
    And the bed group exist
    And the bed group has `15` beds assigned
    When the request to add bed to a group is made
    And the bed is assigned to the group
    Then the user is told the request was successful

  Scenario: Bed does not exist
    Given the application is running
    And a request to add bed to a group
    And valid authentication credentials are being included
    And the bed group exist
    When the request to add bed to a group is made
    Then the bed is not assigned to the group
    And the user is told the bed was not found

  Scenario: Group does not exist
    Given the application is running
    And a request to add bed to a group
    And valid authentication credentials are being included
    And the bed exists
    When the request to add bed to a group is made
    And the user is told the bed group name is not found

  Scenario: Group is already full
    Given the application is running
    And a request to add bed to a group
    And valid authentication credentials are being included
    And the bed exists
    And the bed group exist
    And the bed group has `16` beds assigned
    When the request to add bed to a group is made
    And the user is told the bed group is full
