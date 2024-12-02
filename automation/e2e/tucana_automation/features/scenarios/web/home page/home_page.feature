@WEB @SMOKE
Feature: [WEB] Central Hub displays the organization name and locale date and time

  Background:
    Given Tom goes to "Tucana" Web APP login page
    And Tom sees the version number of the application
    When Tom logs in with his credentials
    Then Tom sees the dashboard

  @SR-1.6.4 @SR-1.6.5 @SR-1.6.14
  Scenario: Central Hub displays the organization name and locale date and time
    And Tom sees the organization name "Sibel Hospital" on page
    And Tom sees the date and time on page


