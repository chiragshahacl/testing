package org.sibel.emulator.gui;

import java.awt.*;
import javax.swing.*;
import org.somda.sdc.biceps.model.participant.ContextAssociation;
import org.somda.sdc.biceps.model.participant.Sex;

public class PatientFormDialog extends JDialog {
    private final JTextField idField = new JTextField();
    private final JTextField givenNameField = new JTextField();
    private final JTextField familyNameField = new JTextField();
    private final JTextField birthDateField = new JTextField();
    private final JComboBox<Sex> genderField = new JComboBox<>(new Sex[] {null, Sex.UNKN, Sex.M, Sex.F, Sex.UNSPEC});
    private final JComboBox<ContextAssociation> associationField = new JComboBox<>(new ContextAssociation[] {
        ContextAssociation.ASSOC, ContextAssociation.NO, ContextAssociation.DIS, ContextAssociation.PRE
    });
    private final JCheckBox validatedByCmsField = new JCheckBox();
    private final JCheckBox validatedByPmField = new JCheckBox();

    private final PatientChangeListener patientChangeListener;

    public PatientFormDialog(Frame owner, PatientChangeListener patientChangeListener) {
        super(owner, "Set Patient Form");

        this.patientChangeListener = patientChangeListener;

        setSize(600, 400);
        setLayout(new BoxLayout(getContentPane(), BoxLayout.Y_AXIS));

        // Fields
        var fieldPanel = new JPanel();
        fieldPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));
        fieldPanel.setLayout(new GridLayout(8, 2));

        fieldPanel.add(new JLabel("Patient ID"));
        fieldPanel.add(idField);
        fieldPanel.add(new JLabel("Given name"));
        fieldPanel.add(givenNameField);
        fieldPanel.add(new JLabel("Family name"));
        fieldPanel.add(familyNameField);
        fieldPanel.add(new JLabel("DOB"));
        fieldPanel.add(birthDateField);
        fieldPanel.add(new JLabel("Gender"));
        fieldPanel.add(genderField);
        fieldPanel.add(new JLabel("Association"));
        fieldPanel.add(associationField);
        fieldPanel.add(new JLabel("Validated by CMS"));
        fieldPanel.add(validatedByCmsField);
        fieldPanel.add(new JLabel("Validated by PM"));
        fieldPanel.add(validatedByPmField);

        // Buttons
        var buttonPanel = new JPanel();

        var cancelButton = new JButton("Cancel");
        cancelButton.addActionListener(e -> {
            this.cancel();
        });
        buttonPanel.add(cancelButton);

        var resetButton = new JButton("Reset");
        resetButton.addActionListener(e -> {
            this.reset();
        });
        buttonPanel.add(resetButton);

        var acceptButton = new JButton("Accept");
        acceptButton.addActionListener(e -> {
            this.accept();
        });
        buttonPanel.add(acceptButton);

        add(fieldPanel);
        add(buttonPanel);

        reset();
    }

    private void cancel() {
        setVisible(false);
        reset();
    }

    private void accept() {
        var patientInfo = new PatientInfo(
                parseBlanks(idField.getText()),
                parseBlanks(givenNameField.getText()),
                parseBlanks(familyNameField.getText()),
                parseBlanks(birthDateField.getText()),
                (Sex) genderField.getSelectedItem(),
                (ContextAssociation) associationField.getSelectedItem(),
                validatedByCmsField.isSelected(),
                validatedByPmField.isSelected());
        patientChangeListener.onPatientChange(patientInfo);
        setVisible(false);
        reset();
    }

    private String parseBlanks(String text) {
        return text != null && !text.isBlank() ? text : null;
    }

    private void reset() {
        idField.setText("");
        givenNameField.setText("");
        familyNameField.setText("");
        birthDateField.setText("");
        genderField.setSelectedIndex(0);
        associationField.setSelectedItem(ContextAssociation.ASSOC);
        validatedByCmsField.setSelected(true);
        validatedByPmField.setSelected(true);
    }
}
