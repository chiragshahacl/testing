package org.sibel.factories;

import org.sibel.PatientMonitor;
import org.somda.sdc.dpws.client.DiscoveredDevice;
import org.somda.sdc.glue.consumer.WatchdogObserver;

public interface PatientMonitorFactory {
    PatientMonitor create(DiscoveredDevice discoveredDevice, WatchdogObserver watchdogObserver);
}
