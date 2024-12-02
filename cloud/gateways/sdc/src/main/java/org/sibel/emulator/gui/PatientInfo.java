package org.sibel.emulator.gui;

import org.somda.sdc.biceps.model.participant.ContextAssociation;
import org.somda.sdc.biceps.model.participant.Sex;

public record PatientInfo(
        String id,
        String givenName,
        String familyName,
        String birthDate,
        Sex gender,
        ContextAssociation association,
        boolean validatedByCms,
        boolean validatedByPm) {}
