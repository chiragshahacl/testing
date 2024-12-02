@WEB @SMOKE @GROUP
Feature: [WEB] Group Management

  Background:
    Given Tom goes to "Tucana" Web APP login page
    And Tom logs in with his credentials
    Then Tom sees the dashboard
    When Tom clicks on "Group Management" Option
    Then Tom sees the "Group Management" Page
    And Tom wants to create a new group

  @SR-1.2.28 @SR-1.2.29 @SR-1.2.31 @SR-1.2.36 @SR-1.2.37 @SR-1.6.9 @SR-1.2.42 @SR-1.2.38 @SR-1.2.39
  Scenario: Create a New Group with default name
    When Tom sees the current group number and clicks on the add a new group sign
    Then Tom sees the new group listed and the group quantity increased
    And Tom sees the default group name was set correctly
    And Tom sees the finish setup button disabled
    When Tom adds two random beds to the group
    Then Tom sees the two random beds added to the group
    When Tom sees the finish setup button enabled
    Then Tom clicks on the finish setup button
    And Tom sees the message regarding a bed ID not being assigned to all patient monitors in the required confirmation pop-up window
    And Tom sees the "Back to edit" button
    And Tom sees the "Confirm" button
    And Tom clicks on confirm setup button
    And Tom is redirected to the home dashboard
    And Tom sees the new group and the beds displayed in the dashboard
    Then Tom clicks on "Group Management" Option
    When Tom deletes the default group added
    Then Tom clicks on the finish setup button
    And Tom clicks on confirm setup button
    Then Tom should not see the last group added anymore
    And Tom logs out

  @SR-1.2.28 @SR-1.2.29 @SR-1.2.35 @SR-1.2.36 @SR-1.2.37 @SR-1.6.9 @SR-1.2.42
  Scenario: Create a New Group with white spaces in the name
    When Tom clicks on the add a new group sign
    Then Tom wants to edit the group name with the name "QAG TEST"
    And Tom sees the finish setup button disabled
    When Tom adds two random beds to the group
    Then Tom sees the two random beds added to the group
    When Tom sees the finish setup button enabled
    Then Tom clicks on the finish setup button
    And Tom clicks on confirm setup button
    And Tom is redirected to the home dashboard
    And Tom sees the new group and the beds displayed in the dashboard
    Then Tom clicks on "Group Management" Option
    And Tom deletes the "QAG TEST" added
    Then Tom clicks on the finish setup button
    And Tom clicks on confirm setup button
    Then Tom should not see the named group anymore
    And Tom logs out

  @SR-1.2.28 @SR-1.2.29 @SR-1.2.30
  Scenario: Create a New Group and set an empty string as a name
    When Tom clicks on the add a new group sign
    Then Tom sees the new group listed
    And Tom deletes the predefined group name and leaves it empty
    Then Tom sees a red outline around the field
    And Tom sees the finish setup button disabled


  @SR-1.2.43
  Scenario: Create a New Group and set already existent group name
    Then Tom sees the existent groups names
    When Tom sees the current group number and clicks on the add a new group sign
    Then Tom sees the new group listed
    And Tom sets one of the already existent group name
    Then Tom adds two random beds to the group
    Then Tom sees a message telling the name is already in use
    And Tom sees the finish setup button disabled


  @SR-1.2.40 @SR-1.2.41
  Scenario: The "Unsaved information" pop-up window has "Back to edit" and "Discard" buttons if a user attempts to exit the “Group Management” view during the edition
    When Tom clicks on the add a new group sign
    Then Tom sees the new group listed
    And Tom sees the default group name was set correctly
    And Tom sees the finish setup button disabled
    When Tom adds two random beds to the group
    Then Tom sees the two random beds added to the group
    When Tom clicks on close modal button
    Then Tom sees the unsaved information popup
    And Tom sees the "Back to edit" button
    And Tom sees the "Discard" button


  @SR-1.2.40 @SR-1.2.41
  Scenario: If you click on "back to edit" button you will be redirected to Bed Management page when a user attempts to exit the “Group Management” view during the edition
    When Tom clicks on the add a new group sign
    Then Tom sees the new group listed
    And Tom sees the default group name was set correctly
    And Tom sees the finish setup button disabled
    When Tom adds two random beds to the group
    Then Tom sees the two random beds added to the group
    When Tom clicks on close modal button
    Then Tom sees the unsaved information popup
    And Tom sees the "Back to edit" button
    When Tom clicks on "Back to edit" button
    Then Tom sees the "Group Management" Page

  @SR-1.2.40 @SR-1.2.41
  Scenario: If you click on "Discard" button you will be redirected to Home Dashboard page when a user attempts to exit the “Group Management” view during the edition
    When Tom clicks on the add a new group sign
    Then Tom sees the new group listed
    And Tom sees the default group name was set correctly
    And Tom sees the finish setup button disabled
    When Tom adds two random beds to the group
    Then Tom sees the two random beds added to the group
    When Tom clicks on close modal button
    Then Tom sees the unsaved information popup
    And Tom sees the "Discard" button
    When Tom clicks on "Discard" button
    Then Tom is redirected to the home dashboard

  @SR-1.2.44
  Scenario: Central Hub displays the error message when a user attempts to add a bed group if any empty bed group exists in the “Group Management” view
    When Tom clicks on the add a new group sign
    And Tom clicks on the add a new group sign
    Then Tom sees the error message "Please first add beds to this group." displayed in group management popup

