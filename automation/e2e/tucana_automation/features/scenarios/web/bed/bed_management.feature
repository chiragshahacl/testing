@WEB @SMOKE @BED
Feature: [WEB] Bed Management

  Background:
    Given Tom goes to "Tucana" Web APP login page
    And Tom logs in with his credentials
    And Tom sees the dashboard
    When Tom clicks on "Bed Management" Option
    Then Tom sees the "Bed Management" Page

  @SR-1.2.2 @SR-1.2.4 @SR-1.2.8 @SR-1.2.9 @SR-1.2.10 @SR-1.2.15 @SR-1.2.17 @SR-1.2.18 @SR-1.2.19 @SR-1.6.8
  Scenario: Create a new bed and delete it
    And Tom wants to create a new bed
    When Tom clicks on the add a new bed sign
    And Tom sets the bed's name as "Bed QA-AU-X01"
    And Tom sees the new bed listed at the bottom
    Then Tom clicks on the next setup button
    And Tom sees the STEP 2 assignment page
    Then Tom saves the bed assigned to the patient monitor
    When Tom assigns the new bed to a patient
    Then Tom sees the finish setup button enabled
    And Tom clicks on the finish bed setup button
    Then Tom clicks on confirm
    And Tom is redirected to the home dashboard
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

  @SR-1.2.2 @SR-1.2.4 @SR-1.2.5 @SR-1.2.8 @SR-1.2.15 @SR-1.2.21 @SR-1.6.8 @SR-1.2.20
  Scenario: Edit the name of added bed
    And Tom wants to create a new bed
    When Tom clicks on the add a new bed sign
    And Tom sets the bed's name as "Bed_QA"
    And Tom sees the new bed listed
    And Tom wants to edit the bed's name with a random name
    And Tom sees the edited name listed
    Then Tom clicks on the next setup button
    And Tom sees the STEP 2 assignment page
    And Tom sees the "Back to step 1" button
    And Tom sees the "Finish bed setup" button
    Then Tom saves the bed assigned to the patient monitor
    When Tom assigns the new bed to a patient
    Then Tom sees the finish setup button enabled
    And Tom clicks on the finish bed setup button
    Then Tom clicks on confirm
    And Tom is redirected to the home dashboard
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

  @SR-1.2.6
  Scenario: Display an error message if the bed field is empty
    And Tom wants to create a new bed
    When Tom clicks on the add a new bed sign
    And Tom clicks on the next setup button
    Then Tom sees the error message "Please enter the bed ID." displayed in bed management popup

  @SR-1.2.7
  Scenario: Display an error message if the bed name is duplicated
    And Tom wants to create a new bed
    When Tom clicks on the add a new bed sign
    And Tom sets the bed's name as "Bed_QA_Duplicated"
    And Tom sees the new bed listed
    When Tom clicks on the add a new bed with the same name
    And Tom sets the bed's name as "Bed_QA_Duplicated"
    And Tom sees the new bed listed
    And Tom clicks on the next setup button
    Then Tom sees the error message "Bed ID already exists. Change or enter a new one." displayed in bed management popup

  @SR-1.2.13 @SR-1.2.14
  Scenario: The "Unsaved information" pop-up window has "Back to edit" and "Discard" buttons if a user attempts to exit the “Bed Management” view during the edition
    And Tom wants to create a new bed
    When Tom clicks on the add a new bed sign
    And Tom sets the bed's name as "Bed_QA_New"
    And Tom sees the new bed listed
    When Tom clicks on close modal button
    Then Tom sees the unsaved information popup
    And Tom sees the "Back to edit" button
    And Tom sees the "Discard" button

  @SR-1.2.24 @SR-1.2.25
  Scenario: The "Unsaved information" pop-up window has "Back to edit" and "Discard" buttons if a user attempts to exit the “Bed Management” view during the mapping
    When Tom clicks on close modal button
    Then Tom sees the unsaved information popup
    And Tom sees the "Back to edit" button
    And Tom sees the "Discard" button

  @SR-1.2.13 @SR-1.2.14
  Scenario: If you click on "back to edit" button you will be redirected to Bed Management page when a user attempts to exit the “Bed Management” view during the edition
    And Tom wants to create a new bed
    When Tom clicks on the add a new bed sign
    And Tom sets the bed's name as "Bed_QA_New"
    And Tom sees the new bed listed
    When Tom clicks on close modal button
    Then Tom sees the unsaved information popup
    And Tom sees the "Back to edit" button
    When Tom clicks on "Back to edit" button
    Then Tom sees the "Bed Management" Page

  @SR-1.2.13 @SR-1.2.14
  Scenario: If you click on "Discard" button you will be redirected to Home Dashboard page when a user attempts to exit the “Bed Management” view during the edition
    And Tom wants to create a new bed
    When Tom clicks on the add a new bed sign
    And Tom sets the bed's name as "Bed_QA_New1"
    And Tom sees the new bed listed
    When Tom clicks on close modal button
    Then Tom sees the unsaved information popup
    And Tom sees the "Discard" button
    When Tom clicks on "Discard" button
    Then Tom is redirected to the home dashboard

  @SR-1.2.24 @SR-1.2.25
  Scenario: If you click on "back to edit" button you will be redirected to Bed Management page when a user attempts to exit the “Bed Management” view during the mapping
    When Tom clicks on close modal button
    Then Tom sees the unsaved information popup
    And Tom sees the "Back to edit" button
    When Tom clicks on "Back to edit" button
    Then Tom sees the "Bed Management" Page

  @SR-1.2.24 @SR-1.2.25
  Scenario: If you click on "Discard" button you will be redirected to Home Dashboard page when a user attempts to exit the “Bed Management” view during the mapping
    When Tom clicks on close modal button
    Then Tom sees the unsaved information popup
    And Tom sees the "Discard" button
    When Tom clicks on "Discard" button
    Then Tom is redirected to the home dashboard

  @SR-1.2.22 @SR-1.2.23 @DD
  Scenario Outline: Central Hub displays the “Confirmation required” pop-up if a user clicks the “Finish bed setup” button if not all patient monitors are assigned to a bed
    Given Tom creates a Patient Monitor "<PM>"
    And Tom wants to create a new bed
    When Tom clicks on the add a new bed sign
    And Tom sets the bed's name as "Bed_QA1"
    And Tom sees the new bed listed
    Then Tom clicks on the next setup button
    And Tom sees the STEP 2 assignment page
    And Tom saves the bed assigned to the patient monitor
    When Tom assigns the new bed to a patient
    Then Tom sees the finish setup button enabled
    When Tom clicks on the finish bed setup button
    Then Tom sees the confirmation required popup
    And Tom sees the message regarding a bed ID not being assigned to all patient monitors in the required confirmation pop-up window
    When Tom clicks on confirm
    And Tom is redirected to the home dashboard
    And Tom clicks on "Bed Management" Option
    And Tom sees the "Bed Management" Page
    And Tom deletes the created bed
    And Tom should not see the bed anymore
    And Tom clicks on the next setup button
    When Tom clicks on the finish bed setup button
    And Tom sees the "Back to edit" button
    And Tom sees the "Confirm" button
    And Tom clicks on confirm
    And Tom restores the bed assigned to the patient monitor
    And Tom deletes a Patient Monitor "<PM>"
    Then Tom sees the finish setup button enabled
    And Tom clicks on the finish bed setup button
    And Tom clicks on confirm
    And Tom logs out


    Examples:
      | PM         |
      | PM-QA-A002 |