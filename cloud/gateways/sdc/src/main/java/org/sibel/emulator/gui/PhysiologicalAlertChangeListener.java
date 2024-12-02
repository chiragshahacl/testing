package org.sibel.emulator.gui;

import java.util.List;
import org.sibel.constants.PhysiologicalAlert;
import org.somda.sdc.biceps.model.participant.AlertSignalPresence;

public interface PhysiologicalAlertChangeListener {
    void onAlertPresenceChanged(List<PhysiologicalAlert> alerts, AlertSignalPresence presence);
}
