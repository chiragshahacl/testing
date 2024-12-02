package org.sibel.emulator.gui;

import org.sibel.constants.SensorType;
import org.sibel.constants.TechnicalAlert;
import org.somda.sdc.biceps.model.participant.AlertSignalPresence;

public interface TechnicalAlertChangeListener {
    void onAlertPresenceChanged(SensorType device, TechnicalAlert alert, AlertSignalPresence presence);
}
