@API @AUTHENTICATION @SMOKE @SR-7.5.3
Feature: [API] Refresh Token

Background:
  Given the user credentials are valid

  Scenario: Refresh Token - validate Refresh Token with a valid refresh token
    Given the Tucana application is running
    And A request to refresh token with a valid refresh token
    And authentication credentials are being included
    When the request is made to refresh token
    Then the user is told the request to refresh the token was successful
    And the user is informed that the new access token is available

  Scenario: Refresh Token - validate Refresh Token with an invalid refresh token
    Given the Tucana application is running
    And A request to refresh token with an invalid refresh token
    And authentication credentials are being included
    When the request is made to refresh token
    Then the user is informed that the request to refresh the token was unauthorized
