Feature: Patient EHR Admission

  Scenario: Successful EHR search patient admission
    Given the application is running
    And a request to admit a patient via EHR search
    And the patient to be upserted does not exist
    And the plan patient admission request is made
    When the request is made to for EHR patient admission
    Then the user is told the request was successful
    And the patient is admitted

  Scenario: EHR search patient patient already monitored
    Given the application is running
    And a request to admit a patient via EHR search
    And the patient to be upserted does not exist
    And the plan patient admission request is made
    And the EHR patient is being monitored
    When the request is made to for EHR patient admission
    Then the user is told the patient is already being monitored

  Scenario: Successful quick admin patient admission
    Given the application is running
    And a request to admit a patient via quick admit
    And the patient to be upserted does not exist
    And the plan patient admission request is made
    When the request is made to for EHR patient admission
    Then the user is told the request was successful
    And the patient is admitted
