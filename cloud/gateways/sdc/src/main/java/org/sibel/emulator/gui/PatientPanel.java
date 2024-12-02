package org.sibel.emulator.gui;

import java.awt.*;
import javax.swing.*;

public class PatientPanel extends JPanel {
    final JLabel idLabel = new JLabel();
    final JLabel givenNameLabel = new JLabel();
    final JLabel familyNameLabel = new JLabel();
    final JLabel birthDateLabel = new JLabel();
    final JLabel genderLabel = new JLabel();
    final JLabel associationLabel = new JLabel();
    final JLabel validatedByCmsLabel = new JLabel();
    final JLabel validatedByPmLabel = new JLabel();

    public PatientPanel() {
        setLayout(new GridLayout(8, 2));

        add(new JLabel("Patient ID"));
        add(idLabel);
        add(new JLabel("Given name"));
        add(givenNameLabel);
        add(new JLabel("Family name"));
        add(familyNameLabel);
        add(new JLabel("DOB"));
        add(birthDateLabel);
        add(new JLabel("Gender"));
        add(genderLabel);
        add(new JLabel("Association"));
        add(associationLabel);
        add(new JLabel("Validated by CMS"));
        add(validatedByCmsLabel);
        add(new JLabel("Validated by PM"));
        add(validatedByPmLabel);
    }

    public void setPatientInfo(PatientInfo patientInfo) {
        idLabel.setText(patientInfo.id());
        givenNameLabel.setText(patientInfo.givenName());
        familyNameLabel.setText(patientInfo.familyName());
        birthDateLabel.setText(patientInfo.birthDate());
        genderLabel.setText(patientInfo.gender() != null ? patientInfo.gender().value() : null);
        associationLabel.setText(
                patientInfo.association() != null ? patientInfo.association().value() : null);
        validatedByCmsLabel.setText(String.valueOf(patientInfo.validatedByCms()));
        validatedByPmLabel.setText(String.valueOf(patientInfo.validatedByPm()));
    }
}
