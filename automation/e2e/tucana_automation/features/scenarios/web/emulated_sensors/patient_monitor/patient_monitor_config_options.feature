@WEB @SMOKE
Feature: [WEB] Patient Monitor Connection - Config Options

@PATIENT_MONITOR @CONFIG
Scenario Outline: Patient Monitor Config Audio Enabled False
  Given Tom creates a Patient Monitor "<PM>"
  And the bed exists
  And the bed group exists
  And the bed is assigned to the group
  And the information is saved
  And Tom goes to "Tucana" Web APP login page
  And Tom logs in with his credentials
  And Tom sees the dashboard
  And Tom sees the Bed Group and the bed created and clicks on it
  And Tom sees the "PATIENT MONITOR IS NOT AVAILABLE" message in the bed details
  And Tom sees the "NOT AVAILABLE" message at the left card
  And Tom assigns a Patient Monitor to a bed
  And 1 Patient exists with the following data
  """
  patient:
    id: aaaaaaaa-0000-4444-0000-4a2b97021e34
    given_name: Peter
    family_name: Parker
    gender: male
    active: true
    primary_identifier: PT-QA-A001
    birthDate: "1975-07-06"
  """
  And Tom connects the Patient Monitor "<PM>" to the existent patient with "audio_enabled" config option False
  And Tom should see the "Audio OFF at bedside" message
  And Tom closes a session for the Patient Monitor "<PM>"
  And Tom disconnects the Patient Monitor "<PM>"
  And Tom deletes a Patient Monitor "<PM>"

    Examples:
    | PM           |
    | PM-QA-A001   |


@PATIENT_MONITOR @CONFIG
Scenario Outline: Patient Monitor Config Audio Enabled True
  Given Tom creates a Patient Monitor "<PM>"
  And the bed exists
  And the bed group exists
  And the bed is assigned to the group
  And the information is saved
  And Tom goes to "Tucana" Web APP login page
  And Tom logs in with his credentials
  And Tom sees the dashboard
  And Tom sees the Bed Group and the bed created and clicks on it
  And Tom sees the "PATIENT MONITOR IS NOT AVAILABLE" message in the bed details
  And Tom sees the "NOT AVAILABLE" message at the left card
  And Tom assigns a Patient Monitor to a bed
  And 1 Patient exists with the following data
  """
  patient:
    id: aaaaaaaa-0000-4444-0000-4a2b97021e34
    given_name: Peter
    family_name: Parker
    gender: male
    active: true
    primary_identifier: PT-QA-A001
    birthDate: "1975-07-06"
  """
  And Tom connects the Patient Monitor "<PM>" to the existent patient with "audio_enabled" config option True
  And Tom should not see the "Audio OFF at bedside" message
  And Tom closes a session for the Patient Monitor "<PM>"
  And Tom disconnects the Patient Monitor "<PM>"
  And Tom deletes a Patient Monitor "<PM>"

    Examples:
    | PM           |
    | PM-QA-A001   |