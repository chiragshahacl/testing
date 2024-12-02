package org.sibel.mdib;

import static org.sibel.constants.MdibHandles.*;
import static org.sibel.mdib.MdibCodedValueFactory.createCodedValue;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.time.Duration;
import java.util.Collection;
import java.util.List;
import org.sibel.constants.*;
import org.sibel.mdib.mdpws.SafetyContextDefType;
import org.sibel.mdib.mdpws.SafetyReqType;
import org.sibel.mdib.mdpws.SelectorType;
import org.somda.sdc.biceps.model.extension.ExtensionType;
import org.somda.sdc.biceps.model.participant.*;

public final class MdibDescriptorFactory {
    public static MdsDescriptor createMdsDescriptor() {
        var descriptor = new MdsDescriptor();
        descriptor.setHandle(ROOT_HANDLE);
        descriptor.setType(createCodedValue("69953", "MDC_DEV_MON_PT_PHYSIO_MULTI_PARAM"));
        descriptor.setDescriptorVersion(BigInteger.ZERO);
        descriptor.setSafetyClassification(SafetyClassification.MED_A);
        return descriptor;
    }

    public static SystemContextDescriptor createSystemContextDescriptor() {
        var descriptor = new SystemContextDescriptor();
        descriptor.setHandle(SYSTEM_CONTEXT_HANDLE);
        return descriptor;
    }

    public static PatientContextDescriptor createPatientContextDescriptor() {
        var descriptor = new PatientContextDescriptor();
        descriptor.setHandle(PATIENT_CONTEXT_HANDLE);
        return descriptor;
    }

    public static BatteryDescriptor createBatteryDescriptor(SensorType sensorType, String devicePrimaryIdentifier) {
        var descriptor = new BatteryDescriptor();
        descriptor.setType(createCodedValue(Metric.BATTERY.code, null));
        descriptor.setHandle(getBatteryHandle(sensorType));
        descriptor.setProductionSpecification(
                createDeviceProductionSpecifications(sensorType, devicePrimaryIdentifier));
        return descriptor;
    }

    public static VmdDescriptor createDeviceDescriptor(SensorType sensorType, String devicePrimaryIdentifier) {
        var descriptor = new VmdDescriptor();
        descriptor.setHandle(getDeviceHandle(sensorType));
        descriptor.setProductionSpecification(
                createDeviceProductionSpecifications(sensorType, devicePrimaryIdentifier));
        return descriptor;
    }

    public static ChannelDescriptor createMetricChannelDescriptor(SensorType sensorType, MetricChannel channel) {
        var descriptor = new ChannelDescriptor();
        descriptor.setHandle(getMetricChannelHandle(sensorType, channel));
        return descriptor;
    }

    public static NumericMetricDescriptor createNumericMetricDescriptor(SensorType sensorType, Metric metric) {
        var descriptor = new NumericMetricDescriptor();
        configureMetricDescriptor(descriptor, sensorType, metric);
        descriptor.setResolution(BigDecimal.ONE);
        return descriptor;
    }

    public static EnumStringMetricDescriptor createStringMetricDescriptor(SensorType sensorType, Metric metric) {
        var descriptor = new EnumStringMetricDescriptor();
        configureMetricDescriptor(descriptor, sensorType, metric);
        descriptor.setAllowedValue(metric.allowedValues.stream()
                .map(value -> {
                    var allowedValue = new EnumStringMetricDescriptor.AllowedValue();
                    allowedValue.setType(createCodedValue(value.code(), null));
                    allowedValue.setValue(value.value());
                    return allowedValue;
                })
                .toList());
        return descriptor;
    }

    public static RealTimeSampleArrayMetricDescriptor createRealTimeMetricDescriptor(
            SensorType sensorType, Metric metric, Duration samplePeriod, Duration determinationPeriod) {
        var descriptor = new RealTimeSampleArrayMetricDescriptor();
        configureMetricDescriptor(descriptor, sensorType, metric);
        descriptor.setSamplePeriod(samplePeriod);
        descriptor.setDeterminationPeriod(determinationPeriod);
        descriptor.setResolution(BigDecimal.ONE);
        return descriptor;
    }

    public static AlertSystemDescriptor createAlertSystemDescriptor(SensorType sensorType) {
        var descriptor = new AlertSystemDescriptor();
        descriptor.setHandle(getAlertSystemHandle(sensorType));
        descriptor.setDescriptorVersion(BigInteger.ZERO);
        return descriptor;
    }

    public static LimitAlertConditionDescriptor createAlertConditionDescriptor(
            SensorType sensorType, TechnicalAlert alert) {
        return createAlertConditionDescriptor(sensorType, alert, true);
    }

    public static LimitAlertConditionDescriptor createAlertConditionDescriptor(
            SensorType sensorType, TechnicalAlert alert, boolean withSources) {
        var descriptor = new LimitAlertConditionDescriptor();
        descriptor.setHandle(getAlertConditionHandle(sensorType, alert));
        descriptor.setPriority(alert.priority);
        descriptor.setKind(AlertConditionKind.TEC);
        descriptor.setSource(withSources ? List.of(getMetricHandle(sensorType, alert.metric)) : List.of());
        descriptor.setType(createCodedValue(alert.condition.code, null));
        descriptor.setAutoLimitSupported(true);
        descriptor.setMaxLimits(createMaxLimits(alert.condition.upperLimit, alert.condition.lowerLimit));
        return descriptor;
    }

    public static LimitAlertConditionDescriptor createAlertConditionDescriptor(PhysiologicalAlert alert) {
        var descriptor = new LimitAlertConditionDescriptor();
        descriptor.setHandle(getAlertConditionHandle(alert));
        descriptor.setPriority(alert.priority);
        descriptor.setKind(AlertConditionKind.PHY);
        descriptor.setSource(alert.condition.sources.stream()
                .map(source -> getMetricHandle(source.sensorType(), source.metric()))
                .toList());
        descriptor.setType(createCodedValue(alert.condition.code, null));
        descriptor.setAutoLimitSupported(true);
        descriptor.setMaxLimits(createMaxLimits(alert.condition.upperLimit, alert.condition.lowerLimit));
        return descriptor;
    }

    public static AlertSignalDescriptor createAlertSignalDescriptor(SensorType sensorType, TechnicalAlert alert) {
        var descriptor = new AlertSignalDescriptor();
        descriptor.setHandle(getAlertSignalHandle(sensorType, alert));
        descriptor.setConditionSignaled(getAlertConditionHandle(sensorType, alert));
        descriptor.setManifestation(AlertSignalManifestation.VIS);
        descriptor.setType(createCodedValue(alert.code, null));
        return descriptor;
    }

    public static AlertSignalDescriptor createAlertSignalDescriptor(PhysiologicalAlert alert) {
        var descriptor = new AlertSignalDescriptor();
        descriptor.setHandle(getAlertSignalHandle(alert));
        descriptor.setConditionSignaled(getAlertConditionHandle(alert));
        descriptor.setManifestation(alert.manifestation);
        descriptor.setType(createCodedValue(alert.code, null));
        descriptor.setLatching(true);
        return descriptor;
    }

    public static ScoDescriptor createScoDescriptor(SensorType sensorType) {
        var descriptor = new ScoDescriptor();
        descriptor.setHandle(getScoHandle(sensorType));
        return descriptor;
    }

    public static AbstractOperationDescriptor createOperationDescriptor(
            SensorType sensorType, ScoOperationType operationType, Collection<SelectorType> safetyContextDefElements) {
        AbstractOperationDescriptor descriptor =
                switch (operationType) {
                    case SET_CONTEXT_STATE -> new SetContextStateOperationDescriptor();
                };
        descriptor.setHandle(getOperationHandle(sensorType, operationType));
        descriptor.setOperationTarget(operationType.target);

        if (safetyContextDefElements != null && !safetyContextDefElements.isEmpty()) {
            var safetyContextDef = new SafetyContextDefType();
            safetyContextDef.getSelector().addAll(safetyContextDefElements);

            var safetyReq = new SafetyReqType();
            safetyReq.setSafetyContextDef(safetyContextDef);

            var extension = new ExtensionType();
            extension.setAny(List.of(safetyReq));

            descriptor.setExtension(extension);
        }

        return descriptor;
    }

    private static void configureMetricDescriptor(
            AbstractMetricDescriptor descriptor, SensorType sensorType, Metric metric) {
        descriptor.setHandle(getMetricHandle(sensorType, metric));
        descriptor.setType(createCodedValue(metric.code, null));
        descriptor.setUnit(createCodedValue(metric.unitCode, null));
        descriptor.setMetricCategory(MetricCategory.UNSPEC);
        descriptor.setMetricAvailability(MetricAvailability.INTR);
    }

    private static List<AbstractDeviceComponentDescriptor.ProductionSpecification> createDeviceProductionSpecifications(
            SensorType sensorType, String devicePrimaryIdentifier) {
        return List.of(
                createProductionSpecification(
                        "531969", ProductionSpecCodes.DEVICE_PRIMARY_IDENTIFIER, devicePrimaryIdentifier),
                createProductionSpecification("531972", ProductionSpecCodes.DEVICE_CODE, sensorType.code));
    }

    private static AbstractDeviceComponentDescriptor.ProductionSpecification createProductionSpecification(
            String code, String symbolicName, String productionSpec) {
        var productionSpecification = new AbstractDeviceComponentDescriptor.ProductionSpecification();
        productionSpecification.setSpecType(createCodedValue(code, symbolicName));
        productionSpecification.setProductionSpec(productionSpec);
        return productionSpecification;
    }

    private static Range createMaxLimits(BigDecimal upper, BigDecimal lower) {
        var maxLimits = new Range();
        if (upper != null) {
            maxLimits.setUpper(upper);
        }
        if (lower != null) {
            maxLimits.setLower(lower);
        }
        return maxLimits;
    }
}
