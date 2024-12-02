@API @BED_GROUP @SMOKE @SR-7.5.3
Feature: [API] Get Bed Group List

  Background:
    Given the user credentials are valid

  Scenario: Get bed group list
    Given The tucana application is running
    And some bed groups exist
    When the user wants to get the list of the bed groups
    Then the user is told the request to get the list of the bed group was successful
    And bed group list is received
    And bed groups are removed to keep the application clean

  Scenario: Get bed group list - Authentication not provided
    Given the Tucana application is running
    And authentication credentials are not being included
    When the user wants to get the list of the bed groups
    Then the user is told the request was forbidden

  Scenario: Get bed group list - Invalid credentials
    Given the Tucana application is running
    And authentication credentials are being included
    And the credentials are not valid
    When the user wants to get the list of the bed groups
    Then the user is told the request was unauthorized