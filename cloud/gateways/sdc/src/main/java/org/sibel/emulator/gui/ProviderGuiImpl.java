package org.sibel.emulator.gui;

import java.util.List;
import javax.swing.*;
import org.sibel.constants.PhysiologicalAlert;
import org.sibel.constants.SensorType;
import org.sibel.constants.TechnicalAlert;

public class ProviderGuiImpl implements ProviderGui {
    public final JFrame gui = new JFrame();
    public final PatientPanel patientPanel = new PatientPanel();
    public final PatientFormDialog patientFormDialog;

    private AudioChangeListener audioChangeListener = activation -> {};
    private PatientChangeListener patientChangeListener = patientInfo -> {};
    private EmulationChangeListener emulationChangeListener = running -> {};
    private PhysiologicalAlertChangeListener physiologicalAlertChangeListener = (alert, presence) -> {};
    private TechnicalAlertChangeListener technicalAlertChangeListener = (device, alert, presence) -> {};
    private BatteryChangeListener batteryChangeListener = (value, status) -> {};
    private BodyAngleChangeListener bodyAngleChangeListener = (angle, position) -> {};

    public ProviderGuiImpl() {
        gui.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        gui.setSize(600, 600);

        // Set margin and layout
        var contentPanel = new JPanel();
        contentPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));
        contentPanel.setLayout(new BoxLayout(contentPanel, BoxLayout.Y_AXIS));

        // Audio settings buttons
        var audioPanel = new AudioPanel((activation) -> audioChangeListener.onAudioChanged(activation));
        contentPanel.add(audioPanel);

        // Emulation settings buttons
        var emulationPanel =
                new EmulationPanel((running) -> emulationChangeListener.onEmulationRunningChanged(running));
        contentPanel.add(emulationPanel);

        // Alert panels
        var hrAlertPanel = new PhysiologicalAlertPanel(
                List.of(PhysiologicalAlert.HR_ME__AUD, PhysiologicalAlert.HR_ME__VIS),
                (alert, presence) -> physiologicalAlertChangeListener.onAlertPresenceChanged(alert, presence));
        contentPanel.add(hrAlertPanel);
        var leadOffAlertPanel = new TechnicalAlertPanel(
                SensorType.ANNE_CHEST,
                TechnicalAlert.LEAD_OFF,
                (device, alert, presence) ->
                        technicalAlertChangeListener.onAlertPresenceChanged(device, alert, presence));
        contentPanel.add(leadOffAlertPanel);

        // Battery panel
        var batteryPanel = new BatteryPanel((value, status) -> batteryChangeListener.onBatteryChange(value, status));
        contentPanel.add(batteryPanel);

        // BodyAngle panel
        var bodyAnglePanel =
                new BodyAnglePanel((angle, position) -> bodyAngleChangeListener.onBodyAngleChanged(angle, position));
        contentPanel.add(bodyAnglePanel);

        // Patient data display
        contentPanel.add(patientPanel);

        // Set patient data button
        var setPatientButton = new JButton("Set Patient");
        patientFormDialog =
                new PatientFormDialog(gui, patientInfo -> patientChangeListener.onPatientChange(patientInfo));
        setPatientButton.addActionListener(e -> patientFormDialog.setVisible(true));

        var setPatientButtonPanel = new JPanel();
        setPatientButtonPanel.add(setPatientButton);

        contentPanel.add(setPatientButtonPanel);

        // Set main panel
        gui.setContentPane(contentPanel);
    }

    @Override
    public void open(String title) {
        gui.setTitle(title);
        gui.setVisible(true);
    }

    @Override
    public void setAudioChangeListener(AudioChangeListener audioChangeListener) {
        this.audioChangeListener = audioChangeListener;
    }

    @Override
    public void setPatientChangeListener(PatientChangeListener patientChangeListener) {
        this.patientChangeListener = patientChangeListener;
    }

    @Override
    public void setEmulationChangeListener(EmulationChangeListener emulationChangeListener) {
        this.emulationChangeListener = emulationChangeListener;
    }

    @Override
    public void setPhysiologicalAlertChangeListener(PhysiologicalAlertChangeListener alertChangeListener) {
        physiologicalAlertChangeListener = alertChangeListener;
    }

    @Override
    public void setTechnicalAlertChangeListener(TechnicalAlertChangeListener alertChangeListener) {
        technicalAlertChangeListener = alertChangeListener;
    }

    @Override
    public void setBatteryChangeListener(BatteryChangeListener batteryChangeListener) {
        this.batteryChangeListener = batteryChangeListener;
    }

    @Override
    public void setBodyAngleChangeListener(BodyAngleChangeListener bodyAngleChangeListener) {
        this.bodyAngleChangeListener = bodyAngleChangeListener;
    }

    @Override
    public void setPatientInfo(PatientInfo patientInfo) {
        patientPanel.setPatientInfo(patientInfo);
    }
}
