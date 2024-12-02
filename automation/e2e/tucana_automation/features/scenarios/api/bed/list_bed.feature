@API @BED @SMOKE @SR-7.5.3
Feature: [API] Get Bed List

  Background:
    Given the user credentials are valid

  Scenario: Get bed list
    Given The tucana application is running
    And some beds exist
    When the user wants to get the list of beds
    Then the user is told the request to get the list of beds was successful
    And beds list is received
    And The beds are removed to keep the application clean

  Scenario: Get bed list - Authentication not provided
    Given the Tucana application is running
    And authentication credentials are not being included
    When the user wants to get the list of beds
    Then the user is told the request was forbidden

  Scenario: Get bed list - Invalid credentials
    Given the Tucana application is running
    And authentication credentials are being included
    And the credentials are not valid
    When the user wants to get the list of beds
    Then the user is told the request was unauthorized
