@API @PATIENT @SMOKE @SR-7.5.3
Feature: [API] Get Patient List

  Background:
    Given the user credentials are valid

  Scenario: Get patient list
    Given The tucana application is running
    And some patient exist
    When the user wants to get the list of patients
    Then the user is told the request to get the list of patients was successful
    And patient list is received
    And patients are removed to keep the application clean

  Scenario: Get patient list - Authentication not provided
    Given the Tucana application is running
    And authentication credentials are not being included
    When the user wants to get the list of patients
    Then the user is told the request was forbidden

  Scenario: Get patient list - Invalid credentials
    Given the Tucana application is running
    And authentication credentials are being included
    And the credentials are not valid
    When the user wants to get the list of patients
    Then the user is told the request was unauthorized