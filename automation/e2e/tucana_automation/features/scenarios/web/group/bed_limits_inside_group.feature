@WEB @SMOKE @GROUP
Feature: [WEB] Group Management Bed Limits

  Background:
    Given Tom assures there's at least 20 beds created
    Then Tom goes to "Tucana" Web APP login page
    And Tom logs in with his credentials
    Then Tom sees the dashboard
    When Tom clicks on "Group Management" Option
    Then Tom sees the "Group Management" Page
    And Tom wants to create a new group

  @SR-1.2.33 @SR-1.2.34
  Scenario: Only 16 beds can be assigned to a group
    When Tom clicks on the add a new group sign
    Then Tom sees the new group listed
    And Tom selects 16 beds
    Then Tom tries to select one more but it should be not possible