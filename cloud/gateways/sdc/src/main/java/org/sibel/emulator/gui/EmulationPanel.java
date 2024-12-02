package org.sibel.emulator.gui;

import java.awt.*;
import javax.swing.*;

public class EmulationPanel extends JPanel {
    public EmulationPanel(EmulationChangeListener emulationChangeListener) {
        setLayout(new FlowLayout(FlowLayout.LEFT));

        var emulationLabel = new JLabel("Emulation:");
        add(emulationLabel);

        var onButton = new JButton("Start");
        onButton.addActionListener(e -> emulationChangeListener.onEmulationRunningChanged(true));
        add(onButton);

        var offButton = new JButton("Stop");
        offButton.addActionListener(e -> emulationChangeListener.onEmulationRunningChanged(false));
        add(offButton);
    }
}
