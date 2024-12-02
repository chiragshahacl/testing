@API @BED_GROUP @SMOKE @SR-7.5.3
Feature: [API] Creat bed group

  Background:
    Given the user credentials are valid

  Scenario: Create bed groups
    Given the Tucana application is running
    And A request to create bed groups through Tucana's API
    And authentication credentials are being included
    When the request is made to create bed groups
    Then the user is told the request to create was successful
    And bed groups were created
    And bed groups are removed to keep the application clean


  Scenario: Create bed groups - Invalid payload
    Given the Tucana application is running
    And a request to create bed groups with invalid name "  " in payload
    And authentication credentials are being included
    When the request is made to create bed groups
    Then the user is told their payload is invalid

  Scenario: Create bed groups - Authentication not provided
    Given the Tucana application is running
    And A request to create bed groups through Tucana's API
    And authentication credentials are not being included
    When the request is made to create bed groups
    Then the user is told the request was forbidden

  Scenario: Create bed groups - Invalid credentials
    Given the Tucana application is running
    And A request to create bed groups through Tucana's API
    And authentication credentials are being included
    And the credentials are not valid
    When the request is made to create bed groups
    Then the user is told the request was unauthorized