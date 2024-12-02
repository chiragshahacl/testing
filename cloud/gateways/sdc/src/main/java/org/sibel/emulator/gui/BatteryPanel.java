package org.sibel.emulator.gui;

import java.awt.*;
import javax.swing.*;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.somda.sdc.biceps.model.participant.BatteryState;

public class BatteryPanel extends JPanel {
    protected static final Logger LOG = LogManager.getLogger();

    private final BatteryChangeListener listener;
    private final JTextField valueField = new JTextField();
    private final JComboBox<BatteryState.ChargeStatus> chargeStatusField =
            new JComboBox<>(BatteryState.ChargeStatus.values());

    public BatteryPanel(BatteryChangeListener listener) {
        this.listener = listener;

        setLayout(new BoxLayout(this, BoxLayout.Y_AXIS));

        add(new JLabel("Battery"));
        add(getContentPanel());

        setBorder(BorderFactory.createLineBorder(Color.GRAY));
    }

    private JPanel getContentPanel() {
        var panel = new JPanel();
        panel.setLayout(new FlowLayout(FlowLayout.CENTER));
        panel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        panel.add(new JLabel("Value "));
        valueField.setColumns(5);
        panel.add(valueField);
        panel.add(new JLabel(" Status "));
        panel.add(chargeStatusField);

        panel.add(getConfirmButton(listener));

        return panel;
    }

    private JButton getConfirmButton(BatteryChangeListener listener) {
        var button = new JButton("Confirm");
        button.addActionListener((event) -> {
            try {
                var value = Integer.parseInt(valueField.getText());
                var chargeStatus = (BatteryState.ChargeStatus) chargeStatusField.getSelectedItem();
                listener.onBatteryChange(value, chargeStatus);
            } catch (Exception e) {
                LOG.error("Failed to set battery", e);
            }
        });
        return button;
    }
}
