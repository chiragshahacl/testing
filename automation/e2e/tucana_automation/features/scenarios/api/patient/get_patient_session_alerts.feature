@API @PATIENT @SMOKE
Feature: [API] Get Patient Session Alerts

  @EMULATED_SENSORS @TECHNICAL @ANNE @SR-1.3.2 @SR-1.3.7 @SR-1.3.10 @SR-1.3.22
  Scenario Outline: Get "<Alarm Type>" alerts for patient sessions
    Given Tom creates a Patient Monitor "<PM>"
    And the bed exists
    And Tom assigns a Patient Monitor to a bed
    And the bed group exists
    And the bed is assigned to the group
    And the information is saved
    And 1 Patient exists with the following data
    """
    patient:
      id: aabbccdd-2222-4444-0000-4a2b97021e56
      given_name: Diana
      family_name: Wallace
      gender: female
      active: true
      primary_identifier: PT-QA-X044
      birthDate: "1970-07-06"
    """
    And Tom connects the Patient Monitor "<PM>" to the existent patient
    And Tom connects a sensor to the Patient Monitor "<PM>" with the following data
    """
    device_code: ANNE Chest
    primary_identifier: SEN-QA-X044
    name: ANNE Chest
    """
    And Tom "activate" a "<Alarm Type>" alarm for the sensor "<Sensor Type>" with the code "<Alarm Code>" with priority "<Priority>"
    And Tom "deactivate" a "<Alarm Type>" alarm for the sensor "<Sensor Type>" with the code "<Alarm Code>" with priority "<Priority>"
    When Tom wants to get the patient session alerts
    And Tom is told the get patient session alerts request was successful
    Then Tom verifies that the patient session alerts information is correct
    And Tom disconnects the sensor "<Sensor ID>"
    And Tom closes a session for the Patient Monitor "<PM>"
    And Tom disconnects the Patient Monitor "<PM>"
    And Tom deletes a Patient Monitor "<PM>"
    And Tom deletes all the created scenario data

    Examples:
      | PM         |  Sensor ID   | Sensor Type | Alarm Code | Alarm Type    | Priority |
      | PM-QA-X044 |  SEN-QA-X044 | ANNE Chest  | 258098     | technical     | HI       |
      | PM-QA-X044 |  SEN-QA-X044 | ANNE Chest  | 258050     | Physiological | HI       |