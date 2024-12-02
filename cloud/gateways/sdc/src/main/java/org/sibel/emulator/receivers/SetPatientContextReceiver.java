package org.sibel.emulator.receivers;

import static org.sibel.mdib.MdibDescriptorFactory.createPatientContextDescriptor;

import java.util.List;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.config.Settings;
import org.sibel.emulator.gui.PatientInfo;
import org.sibel.emulator.gui.ProviderGui;
import org.somda.sdc.biceps.common.MdibDescriptionModifications;
import org.somda.sdc.biceps.model.message.InvocationError;
import org.somda.sdc.biceps.model.message.InvocationState;
import org.somda.sdc.biceps.model.participant.*;
import org.somda.sdc.glue.provider.sco.Context;
import org.somda.sdc.glue.provider.sco.IncomingSetServiceRequest;
import org.somda.sdc.glue.provider.sco.InvocationResponse;
import org.somda.sdc.glue.provider.sco.OperationInvocationReceiver;

public class SetPatientContextReceiver implements OperationInvocationReceiver {
    private static final Logger LOG = LogManager.getLogger();

    // TODO: MAKE SURE IT IS THE SAME AS THE PM DEVICE
    // This must be available at compile time, so we cannot use org.sibel.constants.MdibHandles.getOperationHandle
    public static final String SET_CONTEXT_SCO_HANDLE = "sibel.anneone.sco.pm.setPatientContext";

    private final ProviderGui gui;
    private final Settings settings;

    public SetPatientContextReceiver(ProviderGui gui, Settings settings) {
        this.gui = gui;
        this.settings = settings;
    }

    @IncomingSetServiceRequest(operationHandle = SET_CONTEXT_SCO_HANDLE)
    InvocationResponse setPatientContext(Context context, List<AbstractContextState> patientContextStates) {
        var parsedPatients = patientContextStates.stream()
                .map(state -> (PatientContextState) state)
                .map(state -> new PatientInfo(
                        state.getIdentification().stream()
                                .map(InstanceIdentifier::getExtensionName)
                                .findFirst()
                                .orElse(null),
                        state.getCoreData().getGivenname(),
                        state.getCoreData().getFamilyname(),
                        state.getCoreData().getDateOfBirth(),
                        state.getCoreData().getSex(),
                        state.getContextAssociation(),
                        state.getValidator().stream()
                                .map(InstanceIdentifier::getExtensionName)
                                .toList()
                                .contains(settings.CENTRAL_HUB_VALIDATOR_ID()),
                        state.getValidator().stream()
                                .map(InstanceIdentifier::getExtensionName)
                                .toList()
                                .contains(settings.PATIENT_MONITOR_VALIDATOR_ID())))
                .toList();
        LOG.info("Patient change event received: {}", parsedPatients);
        try {
            var patient = (PatientContextState)
                    patientContextStates.stream().findFirst().orElse(null);

            // Update UI
            if (patient != null) {
                gui.setPatientInfo(parsedPatients.stream().findFirst().orElseThrow());
            }

            if (patient != null && patient.getContextAssociation() != ContextAssociation.ASSOC) {
                context.sendSuccessfulReport(InvocationState.FIN);
                return context.createSuccessfulResponse(InvocationState.FIN);
            }

            // Mark all patient contexts as validated by PM
            //            patientContextStates.forEach(state -> {
            //                var pmValidator = new InstanceIdentifier();
            //                pmValidator.setExtensionName(settings.getPatientMonitorValidatorId());
            //
            //                var validators = state.getValidator();
            //                validators.add(pmValidator);
            //
            //                state.setValidator(validators);
            //            });

            var modifications = MdibDescriptionModifications.create();
            modifications.update(createPatientContextDescriptor(), patientContextStates);
            context.getMdibAccess().writeDescription(modifications);

            LOG.info("New patient context successfully changed");

            // Returns ok
            context.sendSuccessfulReport(InvocationState.FIN);
            return context.createSuccessfulResponse(InvocationState.FIN);
        } catch (Exception e) {
            LOG.error("Failed to set new context", e);

            // Returns failure
            var errorMessage = new LocalizedText();
            errorMessage.setValue(e.getMessage());
            errorMessage.setLang("en");
            context.sendUnsuccessfulReport(InvocationState.FAIL, InvocationError.UNSPEC, List.of(errorMessage));
            return context.createUnsuccessfulResponse(
                    InvocationState.FAIL, InvocationError.UNSPEC, List.of(errorMessage));
        }
    }
}
