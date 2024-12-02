package org.sibel.mdib;

import java.util.List;
import java.util.Optional;
import org.sibel.constants.FhirGenders;
import org.sibel.constants.Hl7Genders;
import org.sibel.utils.StringUtils;
import org.somda.sdc.biceps.common.MdibEntity;
import org.somda.sdc.biceps.common.access.MdibAccess;
import org.somda.sdc.biceps.model.participant.*;

public class MdibUtils {
    public static String getValueFromProductionSpec(MdibEntity entity, String symbolicName) {
        return entity.getDescriptor(AbstractDeviceComponentDescriptor.class)
                .map(deviceDescriptor -> getValueFromProductionSpec(deviceDescriptor, symbolicName))
                .orElse(null);
    }

    public static String getValueFromProductionSpec(
            AbstractDeviceComponentDescriptor deviceDescriptor, String symbolicName) {
        return deviceDescriptor.getProductionSpecification().stream()
                .filter(productionSpecification -> productionSpecification
                        .getSpecType()
                        .getSymbolicCodeName()
                        .equals(symbolicName))
                .map(AbstractDeviceComponentDescriptor.ProductionSpecification::getProductionSpec)
                .findFirst()
                .orElse(null);
    }

    public static <D extends AbstractDescriptor> Optional<D> getParentDescriptorByClass(
            MdibAccess mdibAccess, AbstractState state, Class<D> descriptorClass) {
        var handle = state.getDescriptorHandle();
        return handle != null ? getParentDescriptorByClass(mdibAccess, handle, descriptorClass) : Optional.empty();
    }

    public static <D extends AbstractDescriptor> Optional<D> getParentDescriptorByClass(
            MdibAccess mdibAccess, String handle, Class<D> descriptorClass) {
        var entity = mdibAccess.getEntity(handle).orElse(null);
        return entity != null ? getParentDescriptorByClass(mdibAccess, entity, descriptorClass) : Optional.empty();
    }

    public static <D extends AbstractDescriptor> Optional<D> getParentDescriptorByClass(
            MdibAccess mdibAccess, MdibEntity entity, Class<D> descriptorClass) {
        MdibEntity currentEntity = entity;
        while (currentEntity != null
                && !descriptorClass.isAssignableFrom(
                        currentEntity.getDescriptor().getClass())) {
            var parent = currentEntity.getParent().orElse(null);
            if (parent != null) {
                currentEntity = mdibAccess.getEntity(parent).orElse(null);
            } else {
                currentEntity = null;
            }
        }
        @SuppressWarnings("unchecked")
        var descriptor = currentEntity != null ? (D) currentEntity.getDescriptor() : null;
        return Optional.ofNullable(descriptor);
    }

    public static PatientContextState getPatientContextState(MdibAccess mdibAccess) {
        return (PatientContextState) mdibAccess.getContextStates().stream()
                .filter(x -> PatientContextState.class.isAssignableFrom(x.getClass()))
                .filter(x -> ContextAssociation.ASSOC.equals(x.getContextAssociation()))
                .findFirst()
                .orElse(null);
    }

    public static List<VmdDescriptor> getConnectedSensors(MdibAccess mdibAccess) {
        return mdibAccess.findEntitiesByType(VmdDescriptor.class).stream()
                .flatMap(entity -> entity.getDescriptor(VmdDescriptor.class).stream())
                .toList();
    }

    public static List<LimitAlertConditionState> getLimitAlertConditions(MdibAccess mdibAccess) {
        return mdibAccess.findEntitiesByType(LimitAlertConditionDescriptor.class).stream()
                .flatMap(limit -> limit.getStates(LimitAlertConditionState.class).stream())
                .toList();
    }

    public static List<AlertSignalState> getAlerts(MdibAccess mdibAccess, AlertConditionKind alertKind) {
        return mdibAccess.getStatesByType(AlertSignalState.class).stream()
                .filter(alertSignalState -> {
                    try {
                        var alertSignalDescriptor = mdibAccess
                                .getDescriptor(alertSignalState.getDescriptorHandle(), AlertSignalDescriptor.class)
                                .orElseThrow(NullPointerException::new);
                        var alertConditionDescriptor = mdibAccess
                                .getDescriptor(
                                        alertSignalDescriptor.getConditionSignaled(), AlertConditionDescriptor.class)
                                .orElseThrow(NullPointerException::new);
                        return alertConditionDescriptor.getKind() == alertKind;
                    } catch (NullPointerException e) {
                        return false;
                    }
                })
                .toList();
    }

    public static List<AlertSignalState> getDeviceAlerts(MdibAccess mdibAccess, VmdDescriptor deviceDescriptor) {
        var alertSystem = getAlertSystemEntity(mdibAccess, deviceDescriptor);
        List<AlertSignalState> alertSignalStates;
        if (alertSystem != null) {
            alertSignalStates =
                    mdibAccess.getChildrenByType(alertSystem.getHandle(), AlertSignalDescriptor.class).stream()
                            .flatMap(entity -> entity.getFirstState(AlertSignalState.class).stream())
                            .toList();
        } else {
            alertSignalStates = List.of();
        }
        return alertSignalStates;
    }

    public static Sex getSexFromFhirGender(String gender) {
        return gender != null
                ? switch (gender) {
                    case FhirGenders.MALE -> Sex.M;
                    case FhirGenders.FEMALE -> Sex.F;
                    case FhirGenders.OTHER -> Sex.UNSPEC;
                    default -> Sex.UNKN;
                }
                : null;
    }

    public static String getFhirGenderFromSex(Sex sex) {
        return sex != null
                ? switch (sex) {
                    case M -> FhirGenders.MALE;
                    case F -> FhirGenders.FEMALE;
                    case UNSPEC -> FhirGenders.OTHER;
                    default -> FhirGenders.UNKNOWN;
                }
                : FhirGenders.UNKNOWN;
    }

    public static Sex getSexFromHl7Gender(String gender) {
        return gender != null
                ? switch (StringUtils.uppercase(gender)) {
                    case Hl7Genders.MALE -> Sex.M;
                    case Hl7Genders.FEMALE -> Sex.F;
                    case Hl7Genders.AMBIGUOUS, Hl7Genders.OTHER -> Sex.UNSPEC;
                    default -> Sex.UNKN;
                }
                : null;
    }

    private static AlertSystemDescriptor getAlertSystemEntity(MdibAccess mdibAccess, VmdDescriptor deviceDescriptor) {
        return mdibAccess.getChildrenByType(deviceDescriptor.getHandle(), AlertSystemDescriptor.class).stream()
                .flatMap(mdibEntity -> mdibEntity.getDescriptor(AlertSystemDescriptor.class).stream())
                .findFirst()
                .orElse(null);
    }
}
