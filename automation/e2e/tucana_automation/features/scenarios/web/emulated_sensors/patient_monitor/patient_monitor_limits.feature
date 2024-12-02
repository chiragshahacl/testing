@WEB
Feature: [WEB] Bed Management Patient Monitors List Limits

@PATIENT_MONITOR @SR-1.2.16
Scenario: 64 Patient Monitors should be the list limit
  Given Tom verifies the current PM quantity
  Then Tom creates all the remaining PMs to complete the limit system of 64 PM
  And Tom creates one extra Patient Monitor and expects not to see it inside the list
  And Tom goes to "Tucana" Web APP login page
  And Tom logs in with his credentials
  And Tom sees the dashboard
  When Tom clicks on "Bed Management" Option
  Then Tom sees the "Bed Management" Page
  And Tom verifies the current PM quantity inside the Bed Management Page should be 64
  And Tom verifies the extra Patient Monitor is not listed
