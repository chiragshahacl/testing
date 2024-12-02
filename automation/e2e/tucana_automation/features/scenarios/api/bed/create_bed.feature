@API @BED @SMOKE @SR-7.5.3
Feature: [API] Creat Bed using batch

Background:
  Given the user credentials are valid

  Scenario: Create a new bed
    Given the Tucana application is running
    And A request to create a new bed through Tucana's API
    And authentication credentials are being included
    When the request is made to create a bed
    Then the user is told the request to create was successful
    And the bed is created
    And The bed is removed to keep the application clean

  Scenario: Create beds using batch
    Given the Tucana application is running
    And A request to create beds through Tucana's API
    When the request is made to create a bed
    Then the user is told the request to create was successful
    And the beds were created
    And The beds are removed to keep the application clean

  Scenario: Create a new bed - Invalid payload
    Given the Tucana application is running
    And a request to create a bed with invalid name "  " in payload
    And authentication credentials are being included
    When the request is made to create a bed
    Then the user is told their payload is invalid

  Scenario: Create a new bed - Authentication not provided
    Given the Tucana application is running
    And A request to create a new bed through Tucana's API
    And authentication credentials are not being included
    When the request is made to create a bed
    Then the user is told the request was forbidden

  Scenario: Create a new bed - Invalid credentials
    Given the Tucana application is running
    And A request to create a new bed through Tucana's API
    And authentication credentials are being included
    And the credentials are not valid
    When the request is made to create a bed
    Then the user is told the request was unauthorized
