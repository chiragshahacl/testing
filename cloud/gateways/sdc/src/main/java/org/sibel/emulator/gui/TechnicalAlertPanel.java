package org.sibel.emulator.gui;

import java.awt.*;
import javax.swing.*;
import org.sibel.constants.SensorType;
import org.sibel.constants.TechnicalAlert;
import org.somda.sdc.biceps.model.participant.AlertSignalPresence;

public class TechnicalAlertPanel extends JPanel {
    public TechnicalAlertPanel(SensorType device, TechnicalAlert alert, TechnicalAlertChangeListener listener) {
        setLayout(new BoxLayout(this, BoxLayout.Y_AXIS));

        var titleLabel = new JLabel("Technical Alert:");
        add(titleLabel);

        var alertLabel = new JLabel(" - %s, %s (%s)".formatted(device.name(), alert.name(), alert.code));
        add(alertLabel);

        var buttonPanel = new JPanel();
        buttonPanel.setLayout(new FlowLayout(FlowLayout.CENTER));
        add(buttonPanel);

        var onButton = new JButton("On");
        onButton.addActionListener(e -> listener.onAlertPresenceChanged(device, alert, AlertSignalPresence.ON));
        buttonPanel.add(onButton);

        var latchButton = new JButton("Latch");
        latchButton.addActionListener(e -> listener.onAlertPresenceChanged(device, alert, AlertSignalPresence.LATCH));
        buttonPanel.add(latchButton);

        var offButton = new JButton("Off");
        offButton.addActionListener(e -> listener.onAlertPresenceChanged(device, alert, AlertSignalPresence.OFF));
        buttonPanel.add(offButton);

        setBorder(BorderFactory.createLineBorder(Color.GRAY));
    }
}
