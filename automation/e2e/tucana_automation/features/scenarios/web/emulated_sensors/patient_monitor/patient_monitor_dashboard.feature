@WEB @SMOKE
Feature: [WEB] Patient Monitor Dashboard Sessions

@PATIENT_MONITOR @SR-1.6.37 @SR-1.6.38
Scenario Outline: Patient Monitor Open/Close sessions
  Given Tom creates a Patient Monitor "<PM>"
  And the bed exists
  And the bed group exists
  And the bed is assigned to the group
  And the information is saved
  And Tom goes to "Tucana" Web APP login page
  And Tom logs in with his credentials
  And Tom sees the dashboard
  And Tom sees the Bed Group created and clicks on it
  And Tom sees the "PATIENT MONITOR IS NOT AVAILABLE" message in the dashboard
  And Tom assigns a Patient Monitor to a bed
  And 1 Patient exists with the following data
  """
  patient:
    id: bbbbbbbb-1111-4444-0000-4a2b97021e34
    given_name: John
    family_name: Wazowsky
    gender: male
    active: true
    primary_identifier: PT-QA-A002
    birthDate: "1990-07-06"
  """
  And Tom connects the Patient Monitor "<PM>" to the existent patient
  And Tom sees the "NO ANNE CHEST SENSOR PAIRED" message in the dashboard
  And Tom closes a session for the Patient Monitor "<PM>"
  And Tom sees the "NO ACTIVE PATIENT SESSION" message in the dashboard
  And Tom disconnects the Patient Monitor "<PM>"
  And Tom sees the "PATIENT MONITOR IS NOT AVAILABLE" message in the dashboard
  And Tom deletes a Patient Monitor "<PM>"

    Examples:
    | PM         |
    | PM-QA-A002 |