package org.sibel.mdib;

import static org.sibel.constants.MdibHandles.*;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.time.Instant;
import java.util.Collection;
import java.util.List;
import org.sibel.constants.*;
import org.somda.sdc.biceps.model.participant.*;

public class MdibStateFactory {

    public static MdsState createMdsState() {
        var state = new MdsState();
        state.setDescriptorHandle(ROOT_HANDLE);
        state.setDescriptorVersion(BigInteger.ZERO);
        state.setLang("en");
        state.setOperatingMode(MdsOperatingMode.NML);
        state.setStateVersion(BigInteger.ZERO);
        return state;
    }

    public static SystemContextState createSystemContextState() {
        var state = new SystemContextState();
        state.setDescriptorHandle(SYSTEM_CONTEXT_HANDLE);
        return state;
    }

    public static PatientContextState createPatientContextState(
            String patientId,
            String givenName,
            String familyName,
            String birthDate,
            Sex gender,
            ContextAssociation association,
            Collection<String> validators) {
        var identification = new InstanceIdentifier();
        identification.setExtensionName(patientId);
        var state = new PatientContextState();
        state.setIdentification(List.of(identification));
        state.setDescriptorHandle(PATIENT_CONTEXT_HANDLE);
        state.setHandle(PATIENT_CONTEXT_STATE_HANDLE);
        state.setContextAssociation(association);
        if (validators != null) {
            state.setValidator(validators.stream()
                    .map(identifierName -> {
                        var localizedText = new LocalizedText();
                        localizedText.setValue(identifierName);
                        var identifier = new InstanceIdentifier();
                        identifier.setIdentifierName(List.of(localizedText));
                        return identifier;
                    })
                    .toList());
        }
        var coreData = new PatientDemographicsCoreData();
        coreData.setGivenname(givenName);
        coreData.setFamilyname(familyName);
        coreData.setDateOfBirth(birthDate);
        coreData.setSex(gender);
        state.setCoreData(coreData);
        return state;
    }

    public static BatteryState createBatteryState(
            SensorType sensorType, BigDecimal remainingBattery, BatteryState.ChargeStatus chargeStatus) {
        var capacityRemaining = new Measurement();
        capacityRemaining.setMeasuredValue(remainingBattery);
        capacityRemaining.setMeasurementUnit(MdibCodedValueFactory.createCodedValue(Metric.BATTERY.unitCode, null));
        var batteryState = new BatteryState();
        batteryState.setCapacityRemaining(capacityRemaining);
        batteryState.setDescriptorHandle(getBatteryHandle(sensorType));
        batteryState.setChargeStatus(chargeStatus);
        return batteryState;
    }

    public static NumericMetricState createNumericMetricState(
            SensorType sensorType, Metric metric, BigDecimal value, Instant determinationTime) {
        return createNumericMetricState(sensorType, metric, value, determinationTime, MeasurementValidity.VLD);
    }

    public static NumericMetricState createNumericMetricState(
            SensorType sensorType,
            Metric metric,
            BigDecimal value,
            Instant determinationTime,
            MeasurementValidity validity) {
        var metricValue = new NumericMetricValue();
        metricValue.setValue(value);
        metricValue.setDeterminationTime(determinationTime);
        metricValue.setMetricQuality(createMetricQuality(validity));
        var deviceMetricState = new NumericMetricState();
        deviceMetricState.setDescriptorHandle(getMetricHandle(sensorType, metric));
        deviceMetricState.setMetricValue(metricValue);
        return deviceMetricState;
    }

    public static EnumStringMetricState createStringMetricState(
            SensorType sensorType, Metric metric, String value, Instant determinationTime) {
        return createStringMetricState(sensorType, metric, value, determinationTime, MeasurementValidity.VLD);
    }

    public static EnumStringMetricState createStringMetricState(
            SensorType sensorType,
            Metric metric,
            String value,
            Instant determinationTime,
            MeasurementValidity validity) {
        var metricValue = new StringMetricValue();
        metricValue.setValue(value);
        metricValue.setDeterminationTime(determinationTime);
        metricValue.setMetricQuality(createMetricQuality(validity));
        var deviceMetricState = new EnumStringMetricState();
        deviceMetricState.setDescriptorHandle(getMetricHandle(sensorType, metric));
        deviceMetricState.setMetricValue(metricValue);
        return deviceMetricState;
    }

    public static RealTimeSampleArrayMetricState createRealTimeMetricState(
            SensorType sensorType, Metric metric, List<BigDecimal> samples, Instant determinationTime) {
        var metricValue = new SampleArrayValue();
        metricValue.setSamples(samples);
        metricValue.setDeterminationTime(determinationTime);
        metricValue.setMetricQuality(createMetricQuality());
        var deviceMetricState = new RealTimeSampleArrayMetricState();
        deviceMetricState.setDescriptorHandle(getMetricHandle(sensorType, metric));
        deviceMetricState.setMetricValue(metricValue);
        return deviceMetricState;
    }

    public static VmdState createDeviceState(SensorType sensorType) {
        var deviceState = new VmdState();
        deviceState.setDescriptorHandle(getDeviceHandle(sensorType));
        return deviceState;
    }

    public static ChannelState createChannelState(SensorType sensorType, MetricChannel channel) {
        var deviceMetricChannelState = new ChannelState();
        deviceMetricChannelState.setDescriptorHandle(getMetricChannelHandle(sensorType, channel));
        return deviceMetricChannelState;
    }

    public static AlertSystemState createAlertSystemState(SensorType sensorType, AlertActivation audioActivation) {
        var state = new AlertSystemState();
        state.setDescriptorHandle(getAlertSystemHandle(sensorType));
        state.setSystemSignalActivation(List.of(
                createSystemSignalActivation(AlertSignalManifestation.AUD, audioActivation),
                createSystemSignalActivation(AlertSignalManifestation.VIS, AlertActivation.ON)));
        state.setActivationState(AlertActivation.ON);
        return state;
    }

    private static SystemSignalActivation createSystemSignalActivation(
            AlertSignalManifestation manifestation, AlertActivation activation) {
        var signalActivation = new SystemSignalActivation();
        signalActivation.setManifestation(manifestation);
        signalActivation.setState(activation);
        return signalActivation;
    }

    public static LimitAlertConditionState createAlertConditionState(
            SensorType sensorType, TechnicalAlert alert, boolean enabled, Instant determinationTime) {
        var state = new LimitAlertConditionState();
        state.setDescriptorHandle(getAlertConditionHandle(sensorType, alert));
        state.setActivationState(AlertActivation.ON);
        state.setMonitoredAlertLimits(AlertConditionMonitoredLimits.ALL);
        state.setLimits(createLimits(alert.condition.upperLimit, alert.condition.lowerLimit));
        state.setPresence(enabled);
        state.setDeterminationTime(determinationTime);
        return state;
    }

    public static LimitAlertConditionState createAlertConditionState(PhysiologicalAlert alert) {
        return createAlertConditionState(alert, null, false);
    }

    public static LimitAlertConditionState createAlertConditionState(
            PhysiologicalAlert alert, Instant determinationTime, Boolean enabled) {
        var state = new LimitAlertConditionState();
        state.setDescriptorHandle(getAlertConditionHandle(alert));
        state.setActivationState(AlertActivation.ON);
        state.setMonitoredAlertLimits(AlertConditionMonitoredLimits.ALL);
        state.setLimits(createLimits(alert.condition.upperLimit, alert.condition.lowerLimit));
        state.setPresence(enabled);
        state.setDeterminationTime(determinationTime);
        return state;
    }

    public static AlertSignalState createAlertState(
            SensorType sensorType, TechnicalAlert alert, boolean enabled, boolean latching) {
        var state = new AlertSignalState();
        state.setDescriptorHandle(getAlertSignalHandle(sensorType, alert));
        state.setActivationState(AlertActivation.ON);
        state.setPresence(
                latching ? AlertSignalPresence.LATCH : enabled ? AlertSignalPresence.ON : AlertSignalPresence.OFF);
        return state;
    }

    public static AlertSignalState createAlertState(PhysiologicalAlert alert, boolean enabled, boolean latching) {
        var state = new AlertSignalState();
        state.setDescriptorHandle(getAlertSignalHandle(alert));
        state.setActivationState(AlertActivation.ON);
        state.setPresence(
                latching ? AlertSignalPresence.LATCH : enabled ? AlertSignalPresence.ON : AlertSignalPresence.OFF);
        return state;
    }

    public static ScoState createScoState(SensorType sensorType) {
        var state = new ScoState();
        state.setDescriptorHandle(getScoHandle(sensorType));
        return state;
    }

    public static AbstractOperationState createOperationState(SensorType sensorType, ScoOperationType operationType) {
        AbstractOperationState state =
                switch (operationType) {
                    case SET_CONTEXT_STATE -> new SetContextStateOperationState();
                };
        state.setOperatingMode(OperatingMode.EN);
        state.setDescriptorHandle(getOperationHandle(sensorType, operationType));
        return state;
    }

    private static AbstractMetricValue.MetricQuality createMetricQuality() {
        return createMetricQuality(MeasurementValidity.VLD);
    }

    private static AbstractMetricValue.MetricQuality createMetricQuality(MeasurementValidity validity) {
        var metricQuality = new AbstractMetricValue.MetricQuality();
        metricQuality.setValidity(validity);
        metricQuality.setMode(GenerationMode.REAL);
        return metricQuality;
    }

    private static Range createLimits(BigDecimal upper, BigDecimal lower) {
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
