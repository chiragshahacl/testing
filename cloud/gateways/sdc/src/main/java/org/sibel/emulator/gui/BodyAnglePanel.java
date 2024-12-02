package org.sibel.emulator.gui;

import java.awt.*;
import java.util.stream.Stream;
import javax.swing.*;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class BodyAnglePanel extends JPanel {
    protected static final Logger LOG = LogManager.getLogger();

    private final BodyAngleChangeListener listener;
    private final JTextField angleField = new JTextField();
    private final JComboBox<String> positionField = new JComboBox<>(
            Stream.of("UPRIGHT", "SUPINE", "PRONE", "RIGHT", "LEFT").toArray(String[]::new));

    public BodyAnglePanel(BodyAngleChangeListener listener) {
        this.listener = listener;

        setLayout(new BoxLayout(this, BoxLayout.Y_AXIS));

        add(new JLabel("Body angle"));
        add(getContentPanel());

        setBorder(BorderFactory.createLineBorder(Color.GRAY));
    }

    private JPanel getContentPanel() {
        var panel = new JPanel();
        panel.setLayout(new FlowLayout(FlowLayout.CENTER));
        panel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        panel.add(new JLabel("Value "));
        angleField.setColumns(5);
        panel.add(angleField);
        panel.add(new JLabel(" Position "));
        panel.add(positionField);

        panel.add(getConfirmButton(listener));

        return panel;
    }

    private JButton getConfirmButton(BodyAngleChangeListener listener) {
        var button = new JButton("Confirm");
        button.addActionListener((event) -> {
            try {
                var angle = Integer.parseInt(angleField.getText());
                var position = (String) positionField.getSelectedItem();
                listener.onBodyAngleChanged(angle, position);
            } catch (Exception e) {
                LOG.error("Failed to set body angle", e);
            }
        });
        return button;
    }
}
