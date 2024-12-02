package org.sibel.sco;

import static org.sibel.mdib.MdibStateFactory.createPatientContextState;

import com.google.common.base.MoreObjects;
import com.google.inject.Inject;
import java.util.List;
import java.util.concurrent.TimeUnit;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.PatientMonitor;
import org.sibel.config.Settings;
import org.sibel.exceptions.ActionOnDisconnectedPatientMonitor;
import org.sibel.exceptions.ScoOperationException;
import org.sibel.models.scoParams.SetPatientContextParams;
import org.somda.sdc.biceps.common.MdibEntity;
import org.somda.sdc.biceps.model.message.InvocationState;
import org.somda.sdc.biceps.model.message.SetContextState;
import org.somda.sdc.biceps.model.message.SetContextStateResponse;
import org.somda.sdc.biceps.model.participant.AbstractContextState;
import org.somda.sdc.biceps.model.participant.AbstractOperationDescriptor;
import org.somda.sdc.biceps.model.participant.SetContextStateOperationDescriptor;
import org.somda.sdc.glue.consumer.sco.ScoTransaction;

public class SetPatientContextScoOperation extends AbstractScoOperation {
    private static final Logger LOG = LogManager.getLogger();

    public static final String OPERATION_NAME = "SetPatientContext";

    public final String centralHubValidatorId;

    @Inject
    public SetPatientContextScoOperation(Settings settings) {
        centralHubValidatorId = settings.CENTRAL_HUB_VALIDATOR_ID();
    }

    @Override
    public String getName() {
        return OPERATION_NAME;
    }

    @Override
    public Class<?> getParamsClass() {
        return SetPatientContextParams.class;
    }

    @Override
    public boolean isEnabledFor(PatientMonitor patientMonitor) throws ScoOperationException {
        try {
            return !patientMonitor
                    .getMdibAccess()
                    .findEntitiesByType(SetContextStateOperationDescriptor.class)
                    .isEmpty();
        } catch (ActionOnDisconnectedPatientMonitor e) {
            throw new ScoOperationException("Cannot check if %s is enabled on %s".formatted(this, patientMonitor));
        }
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this).toString();
    }

    @Override
    protected void execute(PatientMonitor patientMonitor, Object rawParams) throws ScoOperationException {
        try {
            var params = (SetPatientContextParams) rawParams;
            var scoOperationHandle = getOperationDescriptor(patientMonitor).getHandle();

            // Prepare SCO request
            var setPatientContext = new SetContextState();
            var patientContextList = params.patients().stream()
                    .map(patient -> (AbstractContextState) createPatientContextState(
                            patient.primaryIdentifier(),
                            patient.givenName(),
                            patient.familyName(),
                            patient.birthDate(),
                            patient.gender(),
                            patient.association(),
                            List.of(centralHubValidatorId)))
                    .toList();
            setPatientContext.setProposedContextState(patientContextList);
            setPatientContext.setOperationHandleRef(scoOperationHandle);

            // Send SCO request
            var listenableResponse = patientMonitor
                    .getSdcRemoteDevice()
                    .getSetServiceAccess()
                    .invoke(setPatientContext, SetContextStateResponse.class);

            LOG.info("[%s] Set context request sent.".formatted(patientMonitor));

            // Read SCO response
            ScoTransaction<SetContextStateResponse> setPatientContextResponse;
            synchronized (listenableResponse) {
                setPatientContextResponse = listenableResponse.get(2, TimeUnit.SECONDS);
            }

            if (InvocationState.FAIL.equals(
                    setPatientContextResponse.getResponse().getInvocationInfo().getInvocationState())) {
                var invocationErrorMessage = setPatientContextResponse
                        .getResponse()
                        .getInvocationInfo()
                        .getInvocationErrorMessage();
                throw new ScoOperationException(
                        "Set patient context invocation failed: %s".formatted(invocationErrorMessage));
            } else {
                LOG.info("[%s] Set context response success".formatted(patientMonitor));
            }
        } catch (Exception e) {
            throw new ScoOperationException("Error setting PM patient context through SCO execution", e);
        }
    }

    @Override
    protected AbstractOperationDescriptor getOperationDescriptor(PatientMonitor patientMonitor)
            throws ScoOperationException {
        try {
            return (AbstractOperationDescriptor)
                    patientMonitor.getMdibAccess().findEntitiesByType(SetContextStateOperationDescriptor.class).stream()
                            .map(MdibEntity::getDescriptor)
                            .findFirst()
                            .orElseThrow(NullPointerException::new);
        } catch (ActionOnDisconnectedPatientMonitor | NullPointerException e) {
            throw new ScoOperationException("%s not enabled for %s".formatted(this, patientMonitor));
        }
    }
}
