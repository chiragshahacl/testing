package org.sibel.exceptions;

public class FailedToConnectPatientMonitor extends Exception {
    public FailedToConnectPatientMonitor(String deviceEpr) {
        super(String.format("Failed to connect to device with epr address %s", deviceEpr));
    }

    public FailedToConnectPatientMonitor(String deviceEpr, Throwable cause) {
        super(String.format("Failed to connect to device with epr address %s", deviceEpr), cause);
    }
}
