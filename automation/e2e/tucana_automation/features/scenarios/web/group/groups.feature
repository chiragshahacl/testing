@WEB @GROUP @SMOKE
Feature: [WEB] Groups Beds and information

  Background:
    Given Tom goes to "Tucana" Web APP login page
    When Tom logs in with his credentials
    Then Tom sees the dashboard

  @SR-1.2.28 @SR-1.2.32 @SR-1.6.12
  Scenario: Navigate between the groups and check that the groups contain beds
    When Tom clicks on "Group Management" Option
    Then Tom sees the "Group Management" Page
    And Tom saves all groups and beds information
    Then Tom closes the group management modal
    And Tom is redirected to the home dashboard
    And Tom is able to navigate between groups and view assigned beds
    And Tom logs out
