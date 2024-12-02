@API @AUTHENTICATION @SMOKE @SR-7.5.3
Feature: [API] Logout

Background:
  Given the user credentials are valid

  Scenario: Logout - validate Logout endpoint
    Given the Tucana application is running
    And A request to logout with valid password
    And authentication credentials are being included
    When the request is made to logout
    Then the user is informed that the logout was successful

  Scenario: Logout - validate Logout endpoint with invalid password
    Given the Tucana application is running
    And A request to logout with invalid credentials
    And authentication credentials are being included
    When the request is made to logout
    Then the user is told their password is incorrect
    And the user is informed that the session has not been logged out due to invalid password

  Scenario: Logout - Authentication not provided
    Given the Tucana application is running
    And A request to logout with valid password
    And authentication credentials are not being included
    When the request is made to logout
    Then the user is told the request was forbidden

  Scenario: Logout - Invalid credentials
    Given the Tucana application is running
    And A request to logout with valid password
    And authentication credentials are being included
    And the credentials are not valid
    When the request is made to logout
    Then the user is told the request was unauthorized