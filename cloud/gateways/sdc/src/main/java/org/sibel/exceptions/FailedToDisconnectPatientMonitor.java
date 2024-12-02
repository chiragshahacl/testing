package org.sibel.exceptions;

public class FailedToDisconnectPatientMonitor extends Exception {
    public FailedToDisconnectPatientMonitor(String deviceEpr) {
        super(String.format("Failed to disconnect to device with epr address %s", deviceEpr));
    }

    public FailedToDisconnectPatientMonitor(String deviceEpr, Throwable cause) {
        super(String.format("Failed to disconnect to device with epr address %s", deviceEpr), cause);
    }
}
