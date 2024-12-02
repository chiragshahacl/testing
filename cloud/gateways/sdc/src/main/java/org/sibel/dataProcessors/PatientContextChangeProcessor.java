package org.sibel.dataProcessors;

import com.google.inject.Inject;
import com.google.inject.assistedinject.Assisted;
import java.util.Collection;
import java.util.stream.Collectors;
import javax.annotation.Nullable;
import org.sibel.exceptions.ProcessingError;
import org.sibel.models.payloads.internal.PatientPayload;
import org.somda.sdc.biceps.model.participant.InstanceIdentifier;
import org.somda.sdc.biceps.model.participant.LocalizedText;
import org.somda.sdc.biceps.model.participant.PatientContextState;

public class PatientContextChangeProcessor {
    public static final String DEFAULT_EMPTY_PATIENT_DATA_VALUE = "-";

    private final PatientContextState context;

    @Inject
    public PatientContextChangeProcessor(@Assisted @Nullable PatientContextState context) {
        this.context = context;
    }

    public PatientPayload getPatientPayload() throws ProcessingError {
        try {
            if (context == null) {
                return null;
            }

            return new PatientPayload(
                    context.getIdentification().get(0).getExtensionName(),
                    getEffectiveValue(context.getCoreData().getGivenname()),
                    getEffectiveValue(context.getCoreData().getFamilyname()),
                    context.getCoreData().getDateOfBirth(),
                    context.getCoreData().getSex(),
                    context.getContextAssociation(),
                    context.getValidator().stream()
                            .map(InstanceIdentifier::getIdentifierName)
                            .flatMap(Collection::stream)
                            .map(LocalizedText::getValue)
                            .collect(Collectors.toSet()));
        } catch (Exception e) {
            throw new ProcessingError("Error processing patient information.", e);
        }
    }

    // TODO: WE SHOULD HANDLE THIS ON THE FRONTEND, NOT HERE
    private String getEffectiveValue(String value) {
        return value != null && !value.isBlank() ? value : DEFAULT_EMPTY_PATIENT_DATA_VALUE;
    }
}
