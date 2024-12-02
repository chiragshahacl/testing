package org.sibel.emulator.gui;

import java.awt.*;
import javax.swing.*;
import org.somda.sdc.biceps.model.participant.AlertActivation;

public class AudioPanel extends JPanel {
    public AudioPanel(AudioChangeListener audioChangeListener) {
        setLayout(new FlowLayout(FlowLayout.LEFT));

        var audioLabel = new JLabel("Audio:");
        add(audioLabel);

        var onButton = new JButton("On");
        onButton.addActionListener(e -> audioChangeListener.onAudioChanged(AlertActivation.ON));
        add(onButton);

        var offButton = new JButton("Off");
        offButton.addActionListener(e -> audioChangeListener.onAudioChanged(AlertActivation.OFF));
        add(offButton);

        var pausedButton = new JButton("Paused");
        pausedButton.addActionListener(e -> audioChangeListener.onAudioChanged(AlertActivation.PSD));
        add(pausedButton);
    }
}
