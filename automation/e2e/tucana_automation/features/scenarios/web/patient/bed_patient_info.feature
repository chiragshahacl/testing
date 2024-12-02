@WEB @BED
Feature: [WEB] Patient Tabs inside bed details

  @SMOKE @SR-1.3.4 @SR-1.6.18 @SR-1.3.21 @SR-1.3.23 @SR-1.3.20 @SR-1.3.2 @SR-1.3.29
  Scenario Outline: Patient Info tab
    Given Tom creates a Patient Monitor "<PM>"
    And the bed exists
    And Tom assigns a Patient Monitor to a bed
    And the bed group exists
    And the bed is assigned to the group
    And the information is saved
    And 1 Patient exists with the following data
    """
    patient:
      id: aabbccdd-5555-5555-0000-4a2b97021e34
      given_name: Steve
      family_name: Rogers
      gender: male
      active: true
      primary_identifier: PT-QA-X002
      birthDate: "1970-07-06"
    """
    And Tom connects the Patient Monitor "<PM>" to the existent patient
    And Tom connects a sensor to the Patient Monitor "<PM>" with the following data
    """
    device_code: ANNE Chest
    primary_identifier: SEN-QA-X002
    name: ANNE Chest
    """
    And Tom goes to "Tucana" Web APP login page
    Given the user credentials are valid
    And Tom goes to "Tucana" Web APP login page
    And Tom logs in with his credentials
    Then Tom sees the dashboard
    And Tom sees the Bed Group and the bed created and clicks on it
    And Tom closes the Bed detail popup and he sees the Multi-Patient view again
    Then Tom sees the Bed Group and the bed created and clicks on it
    When Tom selects the "Patient Info" tab
    Then Tom sees the ID "<PT>", First Name "<First Name>", Last Name "<Last Name>", Sex "<Sex>", DOB "<DOB>" listed
    Then Tom logs out

  Examples:
    | PM          | PT         | First Name  | Last Name   | Sex     | DOB         |
    | PM-QA-X002  | PT-QA-X002 | Steve       | Rogers      | Male    | 1970-07-06  |



  @SMOKE @SR-1.3.5 @SR-1.6.19 @SR-1.3.21 @SR-1.3.23 @SR-1.3.20 @SR-1.3.2
  Scenario Outline: Vital Management tab Alarms limits
    Given Tom creates a Patient Monitor "<PM>"
    And the bed exists
    And Tom assigns a Patient Monitor to a bed
    And the bed group exists
    And the bed is assigned to the group
    And the information is saved
    And 1 Patient exists with the following data
    """
    patient:
      id: aabbccdd-5555-5555-0000-4a2b97021e34
      given_name: Steve
      family_name: Rogers
      gender: male
      active: true
      primary_identifier: PT-QA-X002
      birthDate: "1970-07-06"
    """
    And Tom connects the Patient Monitor "<PM>" to the existent patient
    And Tom connects a sensor to the Patient Monitor "<PM>" with the following data
    """
    device_code: ANNE Chest
    primary_identifier: SEN-QA-X002
    name: ANNE Chest
    """
    And Tom goes to "Tucana" Web APP login page
    Given the user credentials are valid
    And Tom goes to "Tucana" Web APP login page
    And Tom logs in with his credentials
    Then Tom sees the dashboard
    And Tom sees the Bed Group and the bed created and clicks on it
    When Tom selects the "Alarm Limits" tab
    And Tom sees the following Alarms Names and limits
      | Alarm           | Unit  | Low Limit | High Limit     |
      | HR              | bpm   | 45        | 120            |
      | SpO2            | %     | 85        | 100            |
      | PR              | bpm   | 45        | 120            |
      | RR              | brpm  | 5         | 30             |
      | BODY TEMP       | °F    | 93.2      | 102.2          |
      | SKIN TEMP       | °F    | 93.2      | 102.2          |
      | SYS             | mmHg  | 90        | 160            |
      | DIA             | mmHg  | 50        | 110            |
    Then Tom logs out

  Examples:
    | PM          |
    | PM-QA-X002  |



  @SMOKE @SR-1.3.6 @SR-1.3.21 @SR-1.3.23 @SR-1.3.20 @SR-1.3.2
  Scenario Outline: Patient's sensors, icons and name presence at bed details page
    Given Tom creates a Patient Monitor "<PM>"
    And the bed exists
    And Tom assigns a Patient Monitor to a bed
    And the bed group exists
    And the bed is assigned to the group
    And the information is saved
    And 1 Patient exists with the following data
    """
    patient:
      id: aabbccdd-5555-5555-0000-4a2b97021e34
      given_name: Steve
      family_name: Rogers
      gender: male
      active: true
      primary_identifier: PT-QA-X002
      birthDate: "1970-07-06"
    """
    And Tom connects the Patient Monitor "<PM>" to the existent patient
    And Tom connects a sensor to the Patient Monitor "<PM>" with the following data
    """
    device_code: ANNE Chest
    primary_identifier: SEN-QA-X002
    name: ANNE Chest
    """
    And Tom connects a sensor to the Patient Monitor "<PM>" with the following data
    """
    device_code: Nonin 3150
    primary_identifier: SEN-QA-X004
    name: Nonin 3150
    """
    And Tom connects a sensor to the Patient Monitor "<PM>" with the following data
    """
    device_code: Viatom BP monitor
    primary_identifier: SEN-QA-X005
    name: Viatom BP monitor
    """
    And Tom connects a sensor to the Patient Monitor "<PM>" with the following data
    """
    device_code: DMT Thermometer
    primary_identifier: SEN-QA-X006
    name: DMT Thermometer
    """
    And Tom goes to "Tucana" Web APP login page
    Given the user credentials are valid
    And Tom goes to "Tucana" Web APP login page
    And Tom logs in with his credentials
    Then Tom sees the dashboard
    And Tom sees the Bed Group and the bed created and clicks on it
    Then Tom should see the following Patient's sensors with their correspondant icons
        | Sensor            | Sensor ID   |
        | ANNE Chest        | SEN-QA-X002 |
        | ANNE Limb         | SEN-QA-X003 |
        | Nonin 3150        | SEN-QA-X004 |
        | Viatom BP monitor | SEN-QA-X005 |
        | DMT Thermometer   | SEN-QA-X006 |
    Then Tom logs out

    Examples:
      | PM          |
      | PM-QA-X002  |



  @SMOKE @SR-1.3.3 @SR-1.3.20 @SR-1.3.11 @SR-1.3.2
  Scenario Outline: Patient's vitals information
    Given Tom creates a Patient Monitor "<PM>"
    And the bed exists
    And Tom assigns a Patient Monitor to a bed
    And the bed group exists
    And the bed is assigned to the group
    And the information is saved
    And 1 Patient exists with the following data
    """
    patient:
      id: aabbccdd-5555-5555-0000-4a2b97021e34
      given_name: Steve
      family_name: Rogers
      gender: male
      active: true
      primary_identifier: PT-QA-X002
      birthDate: "1970-07-06"
    """
    And Tom connects the Patient Monitor "<PM>" to the existent patient
    And Tom connects a sensor to the Patient Monitor "<PM>" with the following data
    """
    device_code: ANNE Chest
    primary_identifier: SEN-QA-X002
    name: ANNE Chest
    """
    And Tom connects a sensor to the Patient Monitor "<PM>" with the following data
    """
    device_code: Nonin 3150
    primary_identifier: SEN-QA-X004
    name: Nonin 3150
    """
    And Tom connects a sensor to the Patient Monitor "<PM>" with the following data
    """
    device_code: Viatom BP monitor
    primary_identifier: SEN-QA-X005
    name: Viatom BP monitor
    """
    And Tom connects a sensor to the Patient Monitor "<PM>" with the following data
    """
    device_code: DMT Thermometer
    primary_identifier: SEN-QA-X006
    name: DMT Thermometer
    """
    And Tom goes to "Tucana" Web APP login page
    Given the user credentials are valid
    And Tom goes to "Tucana" Web APP login page
    And Tom logs in with his credentials
    Then Tom sees the dashboard
    And Tom sees the Bed Group and the bed created and clicks on it
    Then Tom should see the following Patient's vitals information
      | Information       |
      | HR (bpm)          |
      | SPO2 (%)          |
      | PR (bpm)          |
      | PI (%)            |
      | RR (brpm)         |
      | FALL              |
      | BODY TEMP (°F)    |
      | SKIN TEMP (°F)    |
      | Position (HHMM)   |
      | NIBP (mmHg)       |
      | ECG               |
      | PLETH             |
      | RR                |
      | PULSE (bpm)       |

    Then Tom logs out

    Examples:
      | PM           |
      | PM-QA-X002   |
