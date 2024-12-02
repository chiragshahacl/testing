Feature: Batch assign beds to group

  Scenario: Batch assign beds to one group
    Given the application is running
    And a request to batch assign beds to a group
    And valid authentication credentials are being included
    And the bed group beds exist
    And the bed group exist
    When the request to batch assign beds to a group is made
    And the beds are the only ones assigned to the group
    And the user is told the request was successful

  Scenario: Batch assign beds to multiple groups
    Given the application is running
    And a request to batch assign beds to a group
    And valid authentication credentials are being included
    And the bed group beds exist
    And the bed group exist
    When the request to batch assign beds to a group is made
    And the beds are the only ones assigned to the group
    And the user is told the request was successful

  Scenario: Group gets full with assignment
    Given the application is running
    And a request to batch assign `16` beds to a group
    And valid authentication credentials are being included
    And the bed group beds exist
    And the bed group exist
    When the request to batch assign beds to a group is made
    And the beds are assigned to the group
    Then the user is told the request was successful

  Scenario: Bed does not exist
    Given the application is running
    And a request to batch assign beds to a group
    And valid authentication credentials are being included
    And the bed group exist
    When the request to batch assign beds to a group is made
    Then the beds are not assigned to the group
    And the user is told the bed was not found

  Scenario: Group does not exist
    Given the application is running
    And a request to batch assign beds to a group
    And valid authentication credentials are being included
    And the bed group beds exist
    When the request to batch assign beds to a group is made
    And the user is told the bed group name is not found

  Scenario: Group is full
    Given the application is running
    And a request to batch assign `17` beds to a group
    And valid authentication credentials are being included
    And the bed group beds exist
    And the bed group exist
    When the request to batch assign beds to a group is made
    And the user is told the bed group is full
