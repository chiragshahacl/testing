package org.sibel.emulator.gui;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class NoGui implements ProviderGui {
    protected static final Logger LOG = LogManager.getLogger();

    @Override
    public void open(String title) {
        LOG.info("Opening GUI: %s".formatted(title));
    }

    @Override
    public void setAudioChangeListener(AudioChangeListener audioChangeListener) {}

    @Override
    public void setPatientChangeListener(PatientChangeListener patientChangeListener) {}

    @Override
    public void setEmulationChangeListener(EmulationChangeListener emulationChangeListener) {}

    @Override
    public void setPhysiologicalAlertChangeListener(PhysiologicalAlertChangeListener alertChangeListener) {}

    @Override
    public void setTechnicalAlertChangeListener(TechnicalAlertChangeListener alertChangeListener) {}

    @Override
    public void setBatteryChangeListener(BatteryChangeListener batteryChangeListener) {}

    @Override
    public void setBodyAngleChangeListener(BodyAngleChangeListener bodyAngleChangeListener) {}

    @Override
    public void setPatientInfo(PatientInfo patientInfo) {
        LOG.info("Patient info: %s".formatted(patientInfo));
    }
}
