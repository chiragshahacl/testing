package org.sibel.emulator.gui;

import org.somda.sdc.biceps.model.participant.AlertActivation;

public interface AudioChangeListener {
    void onAudioChanged(AlertActivation activation);
}
