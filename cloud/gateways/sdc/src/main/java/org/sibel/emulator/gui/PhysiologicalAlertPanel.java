package org.sibel.emulator.gui;

import java.awt.*;
import java.util.List;
import javax.swing.*;
import org.sibel.constants.PhysiologicalAlert;
import org.somda.sdc.biceps.model.participant.AlertSignalPresence;

public class PhysiologicalAlertPanel extends JPanel {
    public PhysiologicalAlertPanel(List<PhysiologicalAlert> alerts, PhysiologicalAlertChangeListener listener) {
        setLayout(new BoxLayout(this, BoxLayout.Y_AXIS));

        var titleLabel = new JLabel("Physiological Alerts:");
        add(titleLabel);

        for (var alert : alerts) {
            var alertLabel = new JLabel(" - %s (%s)".formatted(alert.name(), alert.code));
            add(alertLabel);
        }

        var buttonPanel = new JPanel();
        buttonPanel.setLayout(new FlowLayout(FlowLayout.CENTER));
        add(buttonPanel);

        var onButton = new JButton("On");
        onButton.addActionListener(e -> listener.onAlertPresenceChanged(alerts, AlertSignalPresence.ON));
        buttonPanel.add(onButton);

        var latchButton = new JButton("Latch");
        latchButton.addActionListener(e -> listener.onAlertPresenceChanged(alerts, AlertSignalPresence.LATCH));
        buttonPanel.add(latchButton);

        var offButton = new JButton("Off");
        offButton.addActionListener(e -> listener.onAlertPresenceChanged(alerts, AlertSignalPresence.OFF));
        buttonPanel.add(offButton);

        setBorder(BorderFactory.createLineBorder(Color.GRAY));
    }
}
