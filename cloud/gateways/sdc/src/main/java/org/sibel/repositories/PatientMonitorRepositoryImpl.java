package org.sibel.repositories;

import java.util.Collection;
import java.util.HashMap;
import java.util.Map;
import org.sibel.PatientMonitor;

public class PatientMonitorRepositoryImpl implements PatientMonitorRepository {
    private final Map<String, PatientMonitor> map;

    public PatientMonitorRepositoryImpl() {
        map = new HashMap<>();
    }

    @Override
    public void add(PatientMonitor patientMonitor) {
        map.put(patientMonitor.getSerialNumber(), patientMonitor);
    }

    @Override
    public void remove(String serialNumber) {
        map.remove(serialNumber);
    }

    @Override
    public PatientMonitor getBySerialNumber(String serialNumber) {
        return map.get(serialNumber);
    }

    @Override
    public Collection<PatientMonitor> getAll() {
        return map.values();
    }
}
