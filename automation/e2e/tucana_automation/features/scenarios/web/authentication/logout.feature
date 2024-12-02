@WEB @LOGOUT @SMOKE
Feature: [WEB] Log out from Tucana's Web Page

  @SR-1.1.8 @SR-1.1.9 @SR-1.1.10 @SR-1.1.11 @SR-1.1.14 @SR-1.6.10
  Scenario: Log out with correct Password
    Given Tom goes to "Tucana" Web APP login page
    And Tom logs in with his credentials
    And Tom sees the dashboard
    And Tom goes to settings
    When Tom clicks on log out
    And Tom sees the continue button is disabled
    Then Tom fills the log out password with the correct information
    And Tom sees the continue button is enabled
    And Tom clicks on the confirm button
    Then Tom logs out correctly and is redirected to the login page

  @SR-1.1.12 @SR-1.6.10
  Scenario: Log out with incorrect Password
    Given Tom goes to "Tucana" Web APP login page
    And Tom logs in with his credentials
    And Tom sees the dashboard
    And Tom goes to settings
    When Tom clicks on log out
    Then Tom fills the log out password with the incorrect information
    And Tom clicks on the confirm button
    Then Tom should not be able to logout