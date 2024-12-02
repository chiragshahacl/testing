@API @BED_GROUP @SMOKE @SR-7.5.3
Feature: [API] Assign Beds to a Group

  Background:
    Given the user credentials are valid

  Scenario: Assign Beds to a Group
    Given the Tucana application is running
    And the bed group exists
    And some beds exist
    And A request to assign beds to a Group
    And authentication credentials are being included
    When the request is made to assign beds to a Group
    Then the user is told the request to assign was successful
    When the user wants to get the list of the bed groups
    Then the user is told the request to get the list of the bed group was successful
    And bed group list is received in order to verify the beds to a Group
    And The beds are removed to keep the application clean
    And The bed group is removed to keep the application clean


  Scenario: Assign Beds to a Group - Authentication not provided
    Given the Tucana application is running
    And the bed group exists
    And some beds exist
    And A request to assign beds to a Group
    And authentication credentials are not being included
    When the request is made to assign beds to a Group
    Then the user is told the request was forbidden


  Scenario: Assign Beds to a Group - Invalid credentials
    Given the Tucana application is running
    And the bed group exists
    And some beds exist
    And A request to assign beds to a Group
    And authentication credentials are being included
    And the credentials are not valid
    When the request is made to assign beds to a Group
    Then the user is told the request was unauthorized


  Scenario: Assign Beds to a Group - Invalid payload
    Given the Tucana application is running
    And the bed group exists
    And some beds exist
    And A request to assign beds to a Group
    And authentication credentials are being included
    When the request is made to assign beds to a Group with invalid payload
    Then the user is told their payload is invalid