@WEB @ALARMS @SMOKE @AUDIO
Feature: [WEB] Alarm Audio

  Background:
    Given the user credentials are valid
    And Tom goes to "Tucana" Web APP login page
    When Tom logs in with his credentials
    Then Tom sees the dashboard

  @SR-1.6.22 @SR-1.6.23 @SR-1.6.24 @SR-1.6.25 @SR-1.6.26 @SR-1.6.27 @SR-1.6.36 @SR-1.6.29 @SR-1.6.31 @SR-1.6.33 @SR-1.6.34 @SR-1.6.28 @SR-1.6.32
  Scenario: Alarm audio activation/deactivation
    When Tom sees the actual alarm status
    Then Tom goes to settings
    When Tom clicks on Manage audio alarm
    Then Tom changes the alarm status
    When Tom tries to close the alarm popup
    Then Tom sees the unsaved changes popup and closes it
    Then Tom saves the alarm status
    When Tom fills the alarm status password with the correct information
    And Tom sees the continue button is enabled
    And Tom clicks on the confirm button
    Then Tom sees the alarm status successful modification message
    And Tom verifies the new alarm status
    And Tom goes to settings
    And Tom logs out

  @SR-1.6.32 @SR-1.6.30
  Scenario: Alarm audio activation/deactivation incorrect password
    When Tom sees the actual alarm status
    Then Tom goes to settings
    When Tom clicks on Manage audio alarm
    Then Tom changes the alarm status
    Then Tom saves the alarm status
    Then Tom sees the popup message requiring the admin password
    And Tom sees the popup information about the audio silenced
    When Tom fills the alarm status password with the incorrect information
    And Tom clicks on the confirm button
    And Tom sees the incorrect password message
    And Tom sees the continue button is disabled

  @SR-1.6.7
  Scenario: Alarm audio Pause and Pause Cancellation
    Then Tom confirms the alarm is activated
    Then Tom sees the Pause Alarm button
    When Tom pauses the Alarm sound
    Then Tom sees the 2 minutes countdown
    And Tom deactivate the countdown
    And Tom sees the alarm is "activated"
    And Tom logs out
