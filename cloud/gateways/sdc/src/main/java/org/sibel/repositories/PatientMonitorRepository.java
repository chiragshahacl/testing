package org.sibel.repositories;

import java.util.Collection;
import org.sibel.PatientMonitor;

public interface PatientMonitorRepository {
    void add(PatientMonitor patientMonitor);

    // TODO: Patient monitor should be removed either on the watchdog or the health check
    void remove(String serialNumber);

    PatientMonitor getBySerialNumber(String serialNumber);

    Collection<PatientMonitor> getAll();
}
