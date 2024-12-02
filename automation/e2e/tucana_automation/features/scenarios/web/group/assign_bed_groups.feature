@WEB @SMOKE @BED
Feature: [WEB] Bed Management Groups

  Background:
    Given Tom goes to "Tucana" Web APP login page
    And Tom logs in with his credentials
    Then Tom sees the dashboard
    When Tom clicks on "Bed Management" Option
    Then Tom sees the "Bed Management" Page

  @SR-1.2.2 @SR-1.2.4 @SR-1.2.8 @SR-1.2.9 @SR-1.2.15 @SR-1.2.17 @SR-1.2.18 @SR-1.2.19 @SR-1.2.28 @SR-1.2.29 @SR-1.2.36 @SR-1.2.37
  Scenario: Create and assign a bed to a group
    And Tom wants to create a new bed
    When Tom clicks on the add a new bed sign
    And Tom sets the bed's name as "Bed_QA"
    And Tom sees the new bed listed
    And Tom wants to edit the bed's name with a random name
    And Tom sees the edited name listed
    Then Tom clicks on the next setup button
    And Tom sees the STEP 2 assignment page
    Then Tom saves the bed assigned to the patient monitor
    When Tom assigns the new bed to a patient
    Then Tom sees the finish setup button enabled
    And Tom clicks on the finish bed setup button
    Then Tom clicks on confirm
    And Tom is redirected to the home dashboard
    When Tom clicks on "Group Management" Option
    Then Tom sees the "Group Management" Page
    And Tom wants to create a new group
    Then Tom clicks on the add a new group sign
    And Tom wants to edit the group name with a random name
    And Tom sees the finish setup button disabled
    When Tom adds the created bed to the group
    Then Tom sees the created bed added to the group
    Then Tom sees the finish setup button enabled
    Then Tom clicks on the finish setup button
    Then Tom clicks on confirm setup button
    And Tom is redirected to the home dashboard
    And Tom sees the new group and the new bed displayed in the dashboard
    Then Tom clicks on "Group Management" Option
    When Tom deletes the last group added
    Then Tom clicks on the finish setup button
    Then Tom clicks on confirm setup button
    Then Tom should not see the group anymore
    Then Tom clicks on "Bed Management" Option
    And Tom sees the "Bed Management" Page
    Then Tom deletes the created bed
    And Tom should not see the bed anymore
    Then Tom clicks on the next setup button
    And Tom clicks on the finish bed setup button
    Then Tom clicks on confirm
    Then Tom restores the bed assigned to the patient monitor
    Then Tom sees the finish setup button enabled
    And Tom clicks on the finish bed setup button
    Then Tom clicks on confirm
    And Tom logs out
