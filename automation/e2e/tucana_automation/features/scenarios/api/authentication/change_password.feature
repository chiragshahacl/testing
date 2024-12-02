@API @AUTHENTICATION @SMOKE @SR-7.5.3
Feature: [API] Change Password

Background:
  Given the user credentials are valid

  Scenario: Change Password - validate the minimum size for a password
    Given the Tucana application is running
    And A request to update the password with a password with fewer characters than the minimum requested
    And authentication credentials are being included
    When the request is made to update the password
    Then the user is told their password is invalid
    And the user is told their password is too short

  Scenario: Change Password - Authentication not provided
    Given the Tucana application is running
    And A request to update the password with a numeric password
    And authentication credentials are not being included
    When the request is made to update the password
    Then the user is told the request was forbidden

  Scenario: Change Password - Invalid credentials
    Given the Tucana application is running
    And A request to update the password with a numeric password
    And authentication credentials are being included
    And the credentials are not valid
    When the request is made to update the password
    Then the user is told the request was unauthorized

