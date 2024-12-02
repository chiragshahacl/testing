@API @BED_GROUP @SMOKE @SR-7.5.3
Feature: [API] Assign Beds to a Groups

  Background:
    Given the user credentials are valid

  Scenario: Create three groups of beds and assign 2 beds to each group
    Given the Tucana application is running
    And several beds exist
    And some bed groups exist
    And A request to assign beds to a Groups
    And authentication credentials are being included
    When the request is made to assign beds to a Groups
    Then the user is told the request to assign was successful
    When the user wants to get the list of the bed groups
    Then the user is told the request to get the list of the bed group was successful
    And all bed group list are received in order to verify the beds to a Groups
    And all beds are removed to keep the application clean
    And bed groups are removed to keep the application clean

  Scenario: Assign Beds to a Groups - Authentication not provided
    Given the Tucana application is running
    And several beds exist
    And some bed groups exist
    And A request to assign beds to a Groups
    And authentication credentials are not being included
    When the request is made to assign beds to a Groups
    Then the user is told the request was forbidden
    And all beds are removed to keep the application clean
    And bed groups are removed to keep the application clean

  Scenario: Assign Beds to a Groups - Invalid credentials
    Given the Tucana application is running
    And several beds exist
    And some bed groups exist
    And A request to assign beds to a Groups
    And authentication credentials are being included
    And the credentials are not valid
    When the request is made to assign beds to a Groups
    Then the user is told the request was unauthorized
    And all beds are removed to keep the application clean
    And bed groups are removed to keep the application clean
