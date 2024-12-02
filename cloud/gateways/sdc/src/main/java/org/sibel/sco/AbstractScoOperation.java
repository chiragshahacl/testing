package org.sibel.sco;

import com.google.common.base.MoreObjects;
import java.util.List;
import javax.xml.xpath.XPathExpressionException;
import javax.xml.xpath.XPathFactory;
import org.sibel.PatientMonitor;
import org.sibel.constants.MdpwsConfig;
import org.sibel.exceptions.ScoOperationException;
import org.sibel.mdib.mdpws.SafetyReqType;
import org.sibel.mdib.mdpws.SelectorType;
import org.somda.sdc.biceps.model.participant.AbstractOperationDescriptor;

public abstract class AbstractScoOperation {
    public void run(PatientMonitor patientMonitor, Object rawParams) throws ScoOperationException {
        if (!isEnabledFor(patientMonitor)) {
            throw new ScoOperationException("%s not enabled for %s".formatted(this, patientMonitor));
        }

        validateOperationSafetyReq(getOperationDescriptor(patientMonitor));
        execute(patientMonitor, rawParams);
    }

    public abstract boolean isEnabledFor(PatientMonitor patientMonitor) throws ScoOperationException;

    public abstract String getName();

    public abstract Class<?> getParamsClass();

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this).toString();
    }

    protected abstract void execute(PatientMonitor patientMonitor, Object rawParams) throws ScoOperationException;

    protected abstract AbstractOperationDescriptor getOperationDescriptor(PatientMonitor patientMonitor)
            throws ScoOperationException;

    private static void validateOperationSafetyReq(AbstractOperationDescriptor operationDescriptor)
            throws ScoOperationException {
        if (operationDescriptor.getExtension() != null) {
            for (var extension : operationDescriptor.getExtension().getAny()) {
                // Only validate SafetyReq extensions
                if (SafetyReqType.class.isAssignableFrom(extension.getClass())) {
                    var safetyReqType = (SafetyReqType) extension;
                    var safetyContextDef = safetyReqType.getSafetyContextDef();
                    for (SelectorType selectorType : safetyContextDef.getSelector()) {
                        var xpath = selectorType.getValue();
                        try {
                            // Validates is a valid XPath
                            XPathFactory.newInstance().newXPath().compile(xpath);

                            // Validate the path points to a versioning attribute
                            var xpathParts = List.of(xpath.split("/"));
                            var selectedAttribute = xpathParts.get(xpathParts.size() - 1);
                            if (MdpwsConfig.ALLOWED_MDIB_VERSIONING_ATTRIBUTES.stream()
                                    .noneMatch(selectedAttribute::contains)) {
                                // Here we should display the attributes to the user,
                                // but since we have no messaging directly to the user
                                // we just fail the execution before it is called
                                throw new ScoOperationException(
                                        "Safety requirement Xpath %s not an allowed MDIB versioning attribute"
                                                .formatted(xpath));
                            }
                        } catch (XPathExpressionException e) {
                            throw new ScoOperationException(
                                    "Unable to parse Safety requirement Xpath %s".formatted(xpath), e);
                        }
                    }
                }
            }
        }
    }
}
