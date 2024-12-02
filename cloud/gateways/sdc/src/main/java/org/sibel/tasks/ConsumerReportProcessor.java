package org.sibel.tasks;

import static org.sibel.mdib.MdibUtils.*;

import com.google.common.eventbus.Subscribe;
import com.google.inject.Inject;
import com.google.inject.assistedinject.Assisted;
import com.google.inject.name.Named;
import java.util.*;
import org.apache.commons.lang3.tuple.Pair;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.PatientMonitor;
import org.sibel.config.Settings;
import org.sibel.constants.DI;
import org.sibel.constants.ProductionSpecCodes;
import org.sibel.constants.SensorType;
import org.sibel.dataProcessors.utils.Cache;
import org.sibel.exceptions.*;
import org.sibel.factories.InstantProvider;
import org.sibel.factories.ProcessorFactory;
import org.sibel.factories.UuidProvider;
import org.sibel.models.*;
import org.sibel.models.payloads.*;
import org.sibel.models.payloads.internal.*;
import org.sibel.producers.KafkaMessageProducer;
import org.sibel.repositories.PatientMonitorRepository;
import org.somda.sdc.biceps.common.access.MdibAccess;
import org.somda.sdc.biceps.common.access.MdibAccessObserver;
import org.somda.sdc.biceps.common.event.*;
import org.somda.sdc.biceps.model.participant.*;

/**
 * This class handles incoming reports on the provider.
 *
 * <p>
 * Every incoming report triggers the respective handler, or the generic
 * onUpdate handler if no
 * specialized handler is found.
 */
public class ConsumerReportProcessor implements MdibAccessObserver {
    private static final Logger LOG = LogManager.getLogger();

    private final String patientMonitorId;

    private final KafkaMessageProducer kafkaProducer;
    private final String MESSAGE_BROKER_VITALS_TOPIC;
    private final String MESSAGE_BROKER_DEVICE_TOPIC;
    private final String MESSAGE_BROKER_ALERTS_TOPIC;

    private final Cache<AlertPayload> alertCache;
    private final Cache<VitalsRangePayload> vitalsCache;
    private final PatientMonitorRepository patientMonitorRepository;
    private final UuidProvider uuidProvider;
    private final InstantProvider instantProvider;
    private final ProcessorFactory processorFactory;

    @Inject
    public ConsumerReportProcessor(
            @Assisted String patientMonitorId,
            Settings settings,
            KafkaMessageProducer kafkaProducer,
            @Named(DI.ALERT_CACHE) Cache<AlertPayload> alertCache,
            @Named(DI.VITALS_CACHE) Cache<VitalsRangePayload> vitalsCache,
            PatientMonitorRepository patientMonitorRepository,
            UuidProvider uuidProvider,
            InstantProvider instantProvider,
            ProcessorFactory processorFactory) {
        this.patientMonitorId = patientMonitorId;
        this.alertCache = alertCache;
        this.vitalsCache = vitalsCache;
        this.kafkaProducer = kafkaProducer;
        this.patientMonitorRepository = patientMonitorRepository;
        this.uuidProvider = uuidProvider;
        this.instantProvider = instantProvider;
        this.processorFactory = processorFactory;

        // Initialize constants
        MESSAGE_BROKER_DEVICE_TOPIC = settings.KAFKA_TOPIC_DEVICE();
        MESSAGE_BROKER_VITALS_TOPIC = settings.KAFKA_TOPIC_VITALS();
        MESSAGE_BROKER_ALERTS_TOPIC = settings.KAFKA_TOPIC_ALERT();
    }

    @Subscribe
    void onComponentChange(ComponentStateModificationMessage modificationMessage) {
        try {
            var mdibAccess = modificationMessage.getMdibAccess();
            var states = modificationMessage.getStates().values().stream()
                    .flatMap(Collection::stream)
                    .toList();

            LOG.debug("onComponentChange: {}", states);

            var patientId = getPatientId();
            if (patientId != null) {
                for (var state : states) {
                    var processor = processorFactory.createComponentStateChangeProcessor(
                            mdibAccess, state, patientMonitorId, patientId);
                    try {
                        kafkaProducer.notify(
                                processor.getBatteryBrokerMessage(),
                                MESSAGE_BROKER_VITALS_TOPIC,
                                patientId,
                                processor.getBatteryMessageHeaders());
                    } catch (Exception e) {
                        LOG.error("Unable to send battery data", e);
                    }

                    // The charging status is sent as a separate metric
                    try {
                        kafkaProducer.notify(
                                processor.getBatteryChargingStatusBrokerMessage(),
                                MESSAGE_BROKER_VITALS_TOPIC,
                                patientId,
                                processor.getBatteryStatusMessageHeaders());
                    } catch (Exception e) {
                        LOG.error("Unable to send battery charging status data", e);
                    }
                }
            } else {
                LOG.debug(
                        "onComponentChange not triggered because there is no patient assigned to PM: {}",
                        patientMonitorId);
            }
        } catch (Exception e) {
            LOG.error("Unexpected error processing component state modification", e);
        }
    }

    @Subscribe
    void onMetricChange(MetricStateModificationMessage modificationMessage) {
        try {
            var mdibAccess = modificationMessage.getMdibAccess();
            var states = modificationMessage.getStates().values().stream()
                    .flatMap(Collection::stream)
                    .toList();

            LOG.debug("onMetricChange: {}", states);

            var patientId = getPatientId();
            if (patientId != null) {
                for (var state : states) {
                    try {
                        var processor = processorFactory.createMetricChangeProcessor(mdibAccess, state, patientId);
                        kafkaProducer.notify(
                                processor.getBrokerMessage(),
                                MESSAGE_BROKER_VITALS_TOPIC,
                                patientId,
                                processor.getBrokerMessageHeaders());
                    } catch (Exception error) {
                        LOG.error("Unable to send metric data", error);
                    }
                }
            } else {
                LOG.debug(
                        "Metric change broker message nos sent because there is no patient context for gateway: {}",
                        patientMonitorId);
            }
        } catch (Exception e) {
            LOG.error("Unexpected error processing metric state modification", e);
        }
    }

    @Subscribe
    void onWaveformChange(WaveformStateModificationMessage modificationMessage) {
        try {
            var mdibAccess = modificationMessage.getMdibAccess();
            var states = modificationMessage.getStates().values().stream()
                    .flatMap(Collection::stream)
                    .toList();

            LOG.debug("onWaveformChange: {}", states);

            var patientId = getPatientId();
            if (patientId != null) {
                for (var state : states) {
                    try {
                        var processor = processorFactory.createWaveformChangeProcessor(mdibAccess, state, patientId);
                        var brokerMessage = processor.getBrokerMessage();
                        var headers = processor.getHeaders();
                        kafkaProducer.notify(brokerMessage, MESSAGE_BROKER_VITALS_TOPIC, patientId, headers);
                    } catch (Exception e) {
                        LOG.error("Unable to send waveform data", e);
                    }
                }
            } else {
                LOG.debug(
                        "Waveform change broker message nos sent because there is no patient context for gateway: {}",
                        patientMonitorId);
            }
        } catch (Exception e) {
            LOG.error("Unexpected error processing waveform state modification", e);
        }
    }

    @Subscribe
    void onContextChange(DescriptionModificationMessage modificationMessage) {
        try {
            var patientId = getPatientId();
            var mdib = modificationMessage.getMdibAccess();

            LOG.debug("onContextChange: {}", modificationMessage);

            var vitalsRangePayloadList = new ArrayList<VitalsRangePayload>();
            for (var insertedEntity : modificationMessage.getInsertedEntities()) {
                insertedEntity.getStates().forEach(state -> {
                    // patient info has been added or updated
                    if (PatientContextState.class.isAssignableFrom(state.getClass())) {
                        handlePatientContextChange((PatientContextState) state, null);
                    }
                });
            }
            for (var deletedEntity : modificationMessage.getDeletedEntities()) {
                if (deletedEntity
                        .getDescriptor(AbstractDeviceComponentDescriptor.class)
                        .isPresent()) {
                    LOG.info("Found device to delete");
                    var device = deletedEntity
                            .getDescriptor(AbstractDeviceComponentDescriptor.class)
                            .get();
                    var devicePrimaryIdentifier =
                            getValueFromProductionSpec(device, ProductionSpecCodes.DEVICE_PRIMARY_IDENTIFIER);
                    if (devicePrimaryIdentifier != null) {
                        var message = new SensorRemovedBrokerMessage(
                                uuidProvider.get(),
                                instantProvider.now(),
                                new SensorRemovedPayload(devicePrimaryIdentifier, patientId, instantProvider.now()));
                        kafkaProducer.notify(message, MESSAGE_BROKER_DEVICE_TOPIC, patientMonitorId, null);
                        LOG.info("Published sensor removed event");
                    }
                } else if (!deletedEntity.getStates().isEmpty()) {
                    deletedEntity.getStates().forEach(state -> {
                        if (PatientContextState.class.isAssignableFrom(state.getClass())) {
                            handlePatientContextChange(null, (PatientContextState) state);
                        }
                    });
                }
            }
            for (var updatedEntity : modificationMessage.getUpdatedEntities()) {
                for (var abstractState : updatedEntity.getStates()) {
                    if (PatientContextState.class.isAssignableFrom(abstractState.getClass())) {
                        handlePatientContextChange((PatientContextState) abstractState, null);
                    }
                }

                if (updatedEntity.getDescriptor() instanceof SystemContextDescriptor) {
                    LOG.debug("SystemContext has changed");
                } else if (updatedEntity.getDescriptor() instanceof MdsDescriptor) {
                    if (patientId != null) {
                        // Notify of all connected devices
                        for (var pair : getConnectedSensors(mdib)) {
                            var descriptor = pair.getLeft();
                            var sensorPayload = pair.getRight();
                            var alertSignalStates = getDeviceAlerts(mdib, descriptor);
                            // TODO: The processor can be changed to accept multiple states
                            var alerts = alertSignalStates.stream()
                                    .map(alertSignalState -> {
                                        try {
                                            var processor = processorFactory.createAlertChangeProcessor(
                                                    mdib,
                                                    alertSignalState,
                                                    patientMonitorId,
                                                    SensorType.PM.code,
                                                    patientId);
                                            return processor.getAlertSignalPayload();
                                        } catch (ProcessingError error) {
                                            LOG.warn("Error processing alert", error);
                                        }
                                        return null;
                                    })
                                    .filter(Objects::nonNull)
                                    .toList();
                            var device = new DevicePayload(
                                    sensorPayload, alerts, patientMonitorId, new ConfigPayload(true, false));
                            var message = new DeviceDiscoveredBrokerMessage(
                                    uuidProvider.get(),
                                    this.instantProvider.now(),
                                    new DeviceDiscoveredPayload(device, getPatient()));
                            kafkaProducer.notify(message, MESSAGE_BROKER_DEVICE_TOPIC, patientMonitorId, null);
                        }
                    } else {
                        LOG.debug(
                                "Device discovered message not sent because there is no patient context for gateway: {}",
                                patientMonitorId);
                    }
                } else {
                    var newVitalsRangePayloadList = updatedEntity.getStates().stream()
                            .filter(state -> state instanceof LimitAlertConditionState)
                            .map(state -> (LimitAlertConditionState) state)
                            .map(state -> {
                                try {
                                    return processorFactory
                                            .createVitalRangeProcessor(mdib, state)
                                            .getVitalsRangePayload();
                                } catch (ProcessingError e) {
                                    LOG.warn("Error processing limit alert condition for patient: {}", patientId, e);
                                    return null;
                                }
                            })
                            .filter(Objects::nonNull)
                            .toList();
                    vitalsRangePayloadList.addAll(newVitalsRangePayloadList);
                }
            }

            if (!vitalsRangePayloadList.isEmpty()) {
                if (patientId != null) {
                    kafkaProducer.notify(
                            new NewVitalsRangesBrokerMessage(
                                    uuidProvider.get(),
                                    instantProvider.now(),
                                    new NewVitalsRangesPayload(patientMonitorId, vitalsRangePayloadList)),
                            MESSAGE_BROKER_DEVICE_TOPIC,
                            patientId,
                            null);
                } else {
                    LOG.debug(
                            "New vitals ranges broker message was not sent because there is no patient context for gateway: {}",
                            patientMonitorId);
                }
            }
        } catch (Exception e) {
            LOG.error("Unexpected error processing description modification", e);
        }
    }

    private void handlePatientContextChange(
            PatientContextState newPatientContextState, PatientContextState oldPatientContextState) {
        try {
            var newPatient = processorFactory
                    .createPatientContextProcessor(newPatientContextState)
                    .getPatientPayload();
            var oldPatient = processorFactory
                    .createPatientContextProcessor(oldPatientContextState)
                    .getPatientPayload();
            getPatientMonitor().handlePatientChange(newPatient, oldPatient);
        } catch (Exception e) {
            LOG.error("Error processing new patient context received.", e);
        }
    }

    private List<Pair<VmdDescriptor, SensorPayload>> getConnectedSensors(MdibAccess mdib) {
        return mdib.findEntitiesByType(VmdDescriptor.class).stream()
                .map(entity -> {
                    var descriptor = entity.getDescriptor(VmdDescriptor.class).orElseThrow();
                    var devicePrimaryIdentifier =
                            getValueFromProductionSpec(descriptor, ProductionSpecCodes.DEVICE_PRIMARY_IDENTIFIER);
                    var deviceTypeCode = getValueFromProductionSpec(entity, ProductionSpecCodes.DEVICE_CODE);
                    var payload = new SensorPayload(devicePrimaryIdentifier, deviceTypeCode, deviceTypeCode);
                    return Pair.of(descriptor, payload);
                })
                .toList();
    }

    @Subscribe
    void onAlertChange(AlertStateModificationMessage modificationMessage) {
        try {
            LOG.debug("onAlertChange: {}", modificationMessage.getStates());
            var patientId = getPatientId();

            var newVitalsRangePayloadList = new ArrayList<VitalsRangePayload>();
            for (var entry : modificationMessage.getStates().entrySet()) {
                var states = entry.getValue();
                for (var state : states) {
                    var mdibAccess = modificationMessage.getMdibAccess();
                    if (state instanceof AlertSignalState) {
                        if (patientId != null) {
                            try {
                                var processor = processorFactory.createAlertChangeProcessor(
                                        mdibAccess,
                                        (AlertSignalState) state,
                                        patientMonitorId,
                                        SensorType.PM.code,
                                        patientId);
                                var alertPayload = processor.getAlertSignalPayload();
                                var alertKey = processor.getCacheKey();
                                if (alertCache.hasChanged(patientId, alertKey, alertPayload)) {
                                    alertCache.addOrUpdate(patientId, alertKey, alertPayload);
                                    var physiologicalAlert = processor.getAlertKind() == AlertConditionKind.PHY;
                                    kafkaProducer.notify(
                                            new AlertBrokerMessage(
                                                    uuidProvider.get(), instantProvider.now(), alertPayload),
                                            physiologicalAlert
                                                    ? MESSAGE_BROKER_ALERTS_TOPIC
                                                    : MESSAGE_BROKER_DEVICE_TOPIC,
                                            physiologicalAlert ? patientId : patientMonitorId,
                                            processor.getHeaders());
                                }
                            } catch (Exception e) {
                                LOG.error("Error processing alert change event", e);
                            }
                        } else {
                            LOG.debug(
                                    "Alert broker message was not sent because there is no patient context for gateway: {}",
                                    patientMonitorId);
                        }
                    } else if (state instanceof LimitAlertConditionState) {
                        try {
                            var processor = processorFactory.createVitalRangeProcessor(
                                    mdibAccess, (LimitAlertConditionState) state);
                            var payload = processor.getVitalsRangePayload();
                            if (vitalsCache.hasChanged(patientId, payload.getCode(), payload)) {
                                vitalsCache.addOrUpdate(patientId, payload.getCode(), payload);
                                newVitalsRangePayloadList.add(payload);
                            }
                        } catch (Exception e) {
                            LOG.error("Error processing limit alert condition for patient: {}", patientId, e);
                        }
                    } else if (state instanceof AlertSystemState) {
                        try {
                            var config = getPatientMonitor().getConfigPayload();
                            var configPayload = new PmConfigurationUpdatedPayload(
                                    patientMonitorId, config.audioEnabled(), config.audioPauseEnabled());
                            var brokerMessage = new PmConfigurationUpdatedBrokerMessage(
                                    uuidProvider.get(), instantProvider.now(), configPayload);
                            kafkaProducer.notify(brokerMessage, MESSAGE_BROKER_DEVICE_TOPIC, patientMonitorId, null);
                        } catch (ActionOnDisconnectedPatientMonitor e) {
                            LOG.error("PM config update triggered for disconnected device.", e);
                        }
                    }
                }
            }

            if (!newVitalsRangePayloadList.isEmpty()) {
                if (patientId != null) {
                    var newVitalsRangesPayload =
                            new NewVitalsRangesPayload(patientMonitorId, newVitalsRangePayloadList);
                    var brokerMessage = new NewVitalsRangesBrokerMessage(
                            uuidProvider.get(), instantProvider.now(), newVitalsRangesPayload);
                    kafkaProducer.notify(brokerMessage, MESSAGE_BROKER_DEVICE_TOPIC, patientId, null);
                } else {
                    LOG.debug(
                            "New vitals ranges broker message was not sent because there is no patient context for gateway: {}",
                            patientMonitorId);
                }
            }
        } catch (Exception e) {
            LOG.error("Unexpected error processing alert state modifications", e);
        }
    }

    private PatientMonitor getPatientMonitor() {
        return patientMonitorRepository.getBySerialNumber(patientMonitorId);
    }

    private PatientPayload getPatient() {
        try {
            return getPatientMonitor().getPatient();
        } catch (ActionOnDisconnectedPatientMonitor e) {
            LOG.error("Component change triggered for disconnected device.", e);
        }
        return null;
    }

    private String getPatientId() {
        try {
            return getPatientMonitor().getPatientId();
        } catch (ActionOnDisconnectedPatientMonitor e) {
            LOG.error("Component change triggered for disconnected device.", e);
        }
        return null;
    }
}
