package org.sibel.emulator.gui;

public interface ProviderGui {
    void open(String title);

    void setAudioChangeListener(AudioChangeListener audioChangeListener);

    void setPatientChangeListener(PatientChangeListener patientChangeListener);

    void setEmulationChangeListener(EmulationChangeListener emulationChangeListener);

    void setPhysiologicalAlertChangeListener(PhysiologicalAlertChangeListener alertChangeListener);

    void setTechnicalAlertChangeListener(TechnicalAlertChangeListener alertChangeListener);

    void setBatteryChangeListener(BatteryChangeListener batteryChangeListener);

    void setBodyAngleChangeListener(BodyAngleChangeListener bodyAngleChangeListener);

    void setPatientInfo(PatientInfo patientInfo);
}
