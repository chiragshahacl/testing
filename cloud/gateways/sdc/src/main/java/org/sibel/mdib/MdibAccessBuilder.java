package org.sibel.mdib;

import static org.sibel.constants.MdibHandles.*;
import static org.sibel.mdib.MdibDescriptorFactory.*;
import static org.sibel.mdib.MdibStateFactory.*;

import com.google.inject.Guice;
import com.google.inject.Injector;
import java.math.BigDecimal;
import java.time.Duration;
import java.time.Instant;
import java.util.Collection;
import java.util.List;
import org.sibel.constants.*;
import org.sibel.mdib.mdpws.SelectorType;
import org.somda.sdc.biceps.common.MdibDescriptionModifications;
import org.somda.sdc.biceps.common.storage.PreprocessingException;
import org.somda.sdc.biceps.guice.DefaultBicepsConfigModule;
import org.somda.sdc.biceps.guice.DefaultBicepsModule;
import org.somda.sdc.biceps.model.participant.AlertActivation;
import org.somda.sdc.biceps.model.participant.BatteryState;
import org.somda.sdc.biceps.model.participant.ContextAssociation;
import org.somda.sdc.biceps.model.participant.Sex;
import org.somda.sdc.biceps.provider.access.LocalMdibAccess;
import org.somda.sdc.biceps.provider.access.factory.LocalMdibAccessFactory;
import org.somda.sdc.common.guice.DefaultCommonConfigModule;
import org.somda.sdc.common.guice.DefaultCommonModule;
import org.somda.sdc.dpws.guice.DefaultDpwsModule;
import org.somda.sdc.glue.guice.DefaultGlueConfigModule;
import org.somda.sdc.glue.guice.DefaultGlueModule;
import org.somda.sdc.glue.guice.GlueDpwsConfigModule;

public class MdibAccessBuilder {
    private final MdibDescriptionModifications modification = MdibDescriptionModifications.create();
    private final Injector injector;

    public MdibAccessBuilder() {
        this(Guice.createInjector(
                new DefaultCommonConfigModule(),
                new DefaultGlueModule(),
                new DefaultGlueConfigModule(),
                new DefaultBicepsModule(),
                new DefaultBicepsConfigModule(),
                new DefaultCommonModule(),
                new DefaultDpwsModule(),
                new GlueDpwsConfigModule()));
    }

    public MdibAccessBuilder(Injector injector) {
        this.injector = injector;

        modification.insert(createMdsDescriptor(), createMdsState());
        modification.insert(createSystemContextDescriptor(), createSystemContextState(), ROOT_HANDLE);
    }

    public LocalMdibAccess build() throws PreprocessingException {
        var mdibAccess = injector.getInstance(LocalMdibAccessFactory.class).createLocalMdibAccess();
        mdibAccess.writeDescription(modification);
        return mdibAccess;
    }

    public MdibAccessBuilder addPatient(String patientId, Collection<String> validators) {
        return addPatient(patientId, null, null, null, null, ContextAssociation.ASSOC, validators);
    }

    public MdibAccessBuilder addPatient(
            String patientId,
            String givenName,
            String familyName,
            String birthDate,
            Sex gender,
            ContextAssociation association,
            Collection<String> validators) {
        modification.insert(
                createPatientContextDescriptor(),
                createPatientContextState(patientId, givenName, familyName, birthDate, gender, association, validators),
                SYSTEM_CONTEXT_HANDLE);
        return this;
    }

    public MdibAccessBuilder addBattery(
            SensorType sensorType,
            String devicePrimaryIdentifier,
            BigDecimal remainingBattery,
            BatteryState.ChargeStatus chargeStatus) {
        modification.insert(
                createBatteryDescriptor(sensorType, devicePrimaryIdentifier),
                createBatteryState(sensorType, remainingBattery, chargeStatus),
                ROOT_HANDLE);
        return this;
    }

    public MdibAccessBuilder addDevice(SensorType sensorType, String devicePrimaryIdentifier) {
        modification.insert(
                createDeviceDescriptor(sensorType, devicePrimaryIdentifier),
                createDeviceState(sensorType),
                ROOT_HANDLE);
        return this;
    }

    public MdibAccessBuilder addMetricChannel(SensorType sensorType, MetricChannel channel) {
        modification.insert(
                createMetricChannelDescriptor(sensorType, channel),
                createChannelState(sensorType, channel),
                getDeviceHandle(sensorType));
        return this;
    }

    public MdibAccessBuilder addMetric(
            SensorType sensorType, Metric metric, BigDecimal value, Instant determinationTime) {
        modification.insert(
                createNumericMetricDescriptor(sensorType, metric),
                createNumericMetricState(sensorType, metric, value, determinationTime),
                getMetricChannelHandle(sensorType, metric.channel));
        return this;
    }

    public MdibAccessBuilder addMetric(SensorType sensorType, Metric metric, String value, Instant determinationTime) {
        modification.insert(
                createStringMetricDescriptor(sensorType, metric),
                createStringMetricState(sensorType, metric, value, determinationTime),
                getMetricChannelHandle(sensorType, metric.channel));
        return this;
    }

    public MdibAccessBuilder addRealTimeMetric(
            SensorType sensorType,
            Metric metric,
            List<BigDecimal> samples,
            Duration samplePeriod,
            Duration determinationPeriod,
            Instant determinationTime) {
        modification.insert(
                createRealTimeMetricDescriptor(sensorType, metric, samplePeriod, determinationPeriod),
                createRealTimeMetricState(sensorType, metric, samples, determinationTime),
                getMetricChannelHandle(sensorType, metric.channel));
        return this;
    }

    public MdibAccessBuilder addAlertSystem(SensorType sensorType) {
        return addAlertSystem(sensorType, AlertActivation.ON);
    }

    public MdibAccessBuilder addAlertSystem(SensorType sensorType, AlertActivation audioActivation) {
        modification.insert(
                createAlertSystemDescriptor(sensorType),
                createAlertSystemState(sensorType, audioActivation),
                sensorType == SensorType.PM ? ROOT_HANDLE : getDeviceHandle(sensorType));
        return this;
    }

    public MdibAccessBuilder addAlert(SensorType sensorType, TechnicalAlert alert, boolean enabled) {
        return addAlert(sensorType, alert, enabled, null);
    }

    public MdibAccessBuilder addAlert(
            SensorType sensorType, TechnicalAlert alert, boolean enabled, Instant determinationTime) {
        return addAlert(sensorType, alert, enabled, determinationTime, true);
    }

    public MdibAccessBuilder addAlert(
            SensorType sensorType,
            TechnicalAlert alert,
            boolean enabled,
            Instant determinationTime,
            boolean withSources) {
        var alertConditionDescriptor = createAlertConditionDescriptor(sensorType, alert, withSources);
        if (!modification.isAddedAsInserted(alertConditionDescriptor.getHandle())) {
            modification.insert(
                    alertConditionDescriptor,
                    createAlertConditionState(sensorType, alert, enabled, determinationTime),
                    getAlertSystemHandle(sensorType));
        }
        modification.insert(
                createAlertSignalDescriptor(sensorType, alert),
                createAlertState(sensorType, alert, enabled, false),
                getAlertSystemHandle(sensorType));
        return this;
    }

    public MdibAccessBuilder addAlert(PhysiologicalAlert alert, boolean enabled) {
        return addAlert(alert, enabled, null, false);
    }

    public MdibAccessBuilder addAlert(
            PhysiologicalAlert alert, boolean enabled, Instant determinationTime, boolean latching) {
        var alertConditionDescriptor = createAlertConditionDescriptor(alert);
        if (!modification.isAddedAsInserted(alertConditionDescriptor.getHandle())) {
            modification.insert(
                    alertConditionDescriptor,
                    createAlertConditionState(alert, determinationTime, enabled),
                    getAlertSystemHandle(SensorType.PM));
        }
        modification.insert(
                createAlertSignalDescriptor(alert),
                createAlertState(alert, enabled, latching),
                getAlertSystemHandle(SensorType.PM));
        return this;
    }

    public MdibAccessBuilder addSco(SensorType sensorType) {
        modification.insert(
                createScoDescriptor(sensorType),
                createScoState(sensorType),
                sensorType == SensorType.PM ? ROOT_HANDLE : getDeviceHandle(sensorType));
        return this;
    }

    public MdibAccessBuilder addScoOperation(SensorType sensorType, ScoOperationType scoOperationType) {
        return addScoOperation(sensorType, scoOperationType, null);
    }

    public MdibAccessBuilder addScoOperation(
            SensorType sensorType, ScoOperationType operationType, Collection<SelectorType> safetyReqDefElements) {
        modification.insert(
                createOperationDescriptor(sensorType, operationType, safetyReqDefElements),
                createOperationState(sensorType, operationType),
                getScoHandle(sensorType));
        return this;
    }
}
