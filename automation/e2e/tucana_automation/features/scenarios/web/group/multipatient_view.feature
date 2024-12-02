@WEB @ALARMS @SMOKE
Feature: [WEB] Multipatient View - Alarms and Alerts multiple beds

  @MULTIPLE_BEDS @SR-1.3.13 @SR-1.3.14 @SR-1.3.15
  Scenario Outline: Check Alarms and Alert information in <Quantity> beds inside the group
    Given A request to create <Quantity> beds through Tucana's API
    And the bed group exists
    And The beds are assigned to the group
    And <Quantity> Patients exists
    And <Quantity> Patient Monitor exists
    And <Quantity> Patient Monitors are assigned to the beds
    And <Quantity> Patient Monitors are connected to the existent patients
    And <Quantity> ANNE Chest sensors are connected to the Patient Monitors
    And Tom waits 20 seconds
    And Tom goes to "Tucana" Web APP login page
    And Tom logs in with his credentials
    And Tom sees the dashboard
    And Tom sees the Bed Group created and clicks on it
    And Tom can see that the beds in a group displaying a complete patient information
    And ANNE Chest Technical and Physiological HI priority alarm are trigger for each patient, color, number and text are verified
    And Tom deactivate all sensors alarms

    Examples:
      | Quantity      |
      | 16            |

