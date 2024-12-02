package org.sibel.emulator.gui;

import org.somda.sdc.biceps.model.participant.BatteryState;

public interface BatteryChangeListener {
    void onBatteryChange(int value, BatteryState.ChargeStatus status);
}
