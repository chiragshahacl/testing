package org.sibel;

import static org.sibel.constants.RedisKeys.getSharedPatientIdKey;
import static org.sibel.mdib.MdibUtils.*;

import com.google.common.base.MoreObjects;
import com.google.inject.Inject;
import com.google.inject.assistedinject.Assisted;
import com.google.inject.name.Named;
import io.lettuce.core.SetArgs;
import io.lettuce.core.api.sync.RedisCommands;
import java.util.Collection;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.apis.DeviceApi;
import org.sibel.apis.EhrApi;
import org.sibel.config.Settings;
import org.sibel.constants.DI;
import org.sibel.constants.EncounterStatus;
import org.sibel.constants.ProductionSpecCodes;
import org.sibel.constants.SensorType;
import org.sibel.dataProcessors.utils.Cache;
import org.sibel.exceptions.*;
import org.sibel.factories.ConsumerReportProcessorFactory;
import org.sibel.factories.InstantProvider;
import org.sibel.factories.ProcessorFactory;
import org.sibel.factories.UuidProvider;
import org.sibel.models.*;
import org.sibel.models.api.EhrPatient;
import org.sibel.models.api.EhrSearchCriteria;
import org.sibel.models.payloads.*;
import org.sibel.models.payloads.internal.*;
import org.sibel.models.scoParams.SetPatientContextParams;
import org.sibel.producers.KafkaMessageProducer;
import org.sibel.sco.SetPatientContextScoOperation;
import org.sibel.tasks.ConsumerReportProcessor;
import org.somda.sdc.biceps.common.access.MdibAccess;
import org.somda.sdc.biceps.model.participant.*;
import org.somda.sdc.dpws.client.Client;
import org.somda.sdc.dpws.client.DiscoveredDevice;
import org.somda.sdc.glue.consumer.*;

// TODO: Maybe there is probably a better place for this class rather than here
public class PatientMonitor {
    private static final Logger LOG = LogManager.getLogger();

    private final Settings settings;
    private final Client client;
    private final SdcRemoteDevicesConnector connector;
    private final DiscoveredDevice discoveredDevice;
    private final WatchdogObserver watchdogObserver;
    private final ProcessorFactory processorFactory;
    private final KafkaMessageProducer kafkaProducer;
    private final ConsumerReportProcessorFactory consumerReportProcessorFactory;
    private final DeviceApi deviceApi;
    private final EhrApi ehrApi;
    private final SetPatientContextScoOperation setPatientContextScoOperation;
    private final RedisCommands<String, String> redis;
    private final Cache<AlertPayload> alertsCache;
    private final Cache<VitalsRangePayload> vitalsCache;
    private final UuidProvider uuidProvider;
    private final InstantProvider instantProvider;

    private String serialNumber = null;
    private SdcRemoteDevice sdcRemoteDevice = null;
    private ConsumerReportProcessor consumerReportProcessor = null;

    private final Lock patientLock = new ReentrantLock();
    private PatientPayload validatedPatient = null;

    @Inject
    public PatientMonitor(
            @Assisted DiscoveredDevice discoveredDevice,
            @Assisted WatchdogObserver watchdogObserver,
            @Named(DI.CLIENT) Client client,
            Settings settings,
            SdcRemoteDevicesConnector connector,
            ProcessorFactory processorFactory,
            KafkaMessageProducer kafkaProducer,
            ConsumerReportProcessorFactory consumerReportProcessorFactory,
            DeviceApi deviceApi,
            EhrApi ehrApi,
            SetPatientContextScoOperation setPatientContextScoOperation,
            RedisCommands<String, String> redis,
            @Named(DI.ALERT_CACHE) Cache<AlertPayload> alertsCache,
            @Named(DI.VITALS_CACHE) Cache<VitalsRangePayload> vitalsCache,
            UuidProvider uuidProvider,
            InstantProvider instantProvider) {
        this.client = client;
        this.settings = settings;
        this.connector = connector;
        this.processorFactory = processorFactory;
        this.kafkaProducer = kafkaProducer;
        this.discoveredDevice = discoveredDevice;
        this.watchdogObserver = watchdogObserver;
        this.consumerReportProcessorFactory = consumerReportProcessorFactory;
        this.deviceApi = deviceApi;
        this.ehrApi = ehrApi;
        this.setPatientContextScoOperation = setPatientContextScoOperation;
        this.redis = redis;
        this.alertsCache = alertsCache;
        this.vitalsCache = vitalsCache;
        this.uuidProvider = uuidProvider;
        this.instantProvider = instantProvider;
    }

    public String getSerialNumber() {
        return serialNumber;
    }

    public String getDeviceEpr() {
        return discoveredDevice.getEprAddress();
    }

    public void connect() throws FailedToConnectPatientMonitor {
        try {
            var hostingServiceFuture = client.connect(discoveredDevice);
            var hostingServiceProxy =
                    hostingServiceFuture.get(settings.REMOTE_DEVICE_CONN_MAX_WAIT(), TimeUnit.SECONDS);
            var remoteDeviceFuture = connector.connect(
                    hostingServiceProxy,
                    ConnectConfiguration.create(ConnectConfiguration.ALL_EPISODIC_AND_WAVEFORM_REPORTS));

            sdcRemoteDevice = remoteDeviceFuture.get(settings.REMOTE_DEVICE_CONN_MAX_WAIT(), TimeUnit.SECONDS);
            sdcRemoteDevice.registerWatchdogObserver(watchdogObserver);
            hostingServiceProxy
                    .getThisDevice()
                    .ifPresent(thisDeviceType -> serialNumber = thisDeviceType.getSerialNumber());
        } catch (Exception e) {
            throw new FailedToConnectPatientMonitor(discoveredDevice.getEprAddress(), e);
        }
    }

    public void disconnect() throws FailedToDisconnectPatientMonitor {
        try {
            if (consumerReportProcessor != null) {
                sdcRemoteDevice.getMdibAccessObservable().unregisterObserver(consumerReportProcessor);
                consumerReportProcessor = null;
            }

            sdcRemoteDevice.unregisterWatchdogObserver(watchdogObserver);
            connector.disconnect(discoveredDevice.getEprAddress()).get();
        } catch (Exception e) {
            throw new FailedToDisconnectPatientMonitor(discoveredDevice.getEprAddress(), e);
        }
    }

    public boolean isConnected() {
        return sdcRemoteDevice != null && sdcRemoteDevice.isRunning();
    }

    // Needed for testing
    public void forceConnect(SdcRemoteDevice sdcRemoteDevice, String serialNumber, PatientPayload patient) {
        this.sdcRemoteDevice = sdcRemoteDevice;
        this.serialNumber = serialNumber;
        setValidatedPatient(patient);
    }

    public void notifyDiscovery() throws ActionOnDisconnectedPatientMonitor {
        var patient = getNonValidatedPatient();
        patient = patient != null
                        && !patient.isEmpty()
                        && patient.getAssociation() == ContextAssociation.ASSOC
                        && patient.hasValidators(settings.PATIENT_MONITOR_VALIDATOR_ID())
                ? patient
                : null;

        // Validate patient context association
        var patientAlreadyInUse = checkPatientAlreadyInUse(patient);
        var ongoingEncounter = handleOngoingCentralHubEncounters(patientAlreadyInUse);

        // Notify patient monitor discovery
        var connectedSensorsPayloads = getConnectedSensorsPayloads();
        List<AlertPayload> technicalAlertPayloads = patient != null && !patientAlreadyInUse
                ? getAlertPayloads(patient.getPrimaryIdentifier(), AlertConditionKind.TEC)
                : List.of();
        var config = getConfigPayload();
        var gateway = new DevicePayload(
                serialNumber,
                SensorType.PM.code,
                null,
                SensorType.PM.code,
                connectedSensorsPayloads,
                technicalAlertPayloads,
                config);

        if (patient != null && !patientAlreadyInUse) {
            var physiologicalAlerts = getAlertPayloads(patient.getPrimaryIdentifier(), AlertConditionKind.PHY);
            patient.setAlerts(physiologicalAlerts);
        }

        var deviceDiscoveredMessage = new DeviceDiscoveredBrokerMessage(
                uuidProvider.get(),
                instantProvider.now(),
                new DeviceDiscoveredPayload(gateway, patientAlreadyInUse ? null : patient));
        kafkaProducer.notify(deviceDiscoveredMessage, settings.KAFKA_TOPIC_DEVICE(), serialNumber, null);

        // TODO: THIS SHOULD BE PART OF THE DEVICE DISCOVERED MESSAGE
        // Notify new vital ranges for the patient monitor
        var newVitalsRangesMessage = new NewVitalsRangesBrokerMessage(
                uuidProvider.get(),
                instantProvider.now(),
                new NewVitalsRangesPayload(serialNumber, getVitalsRangePayloads()));
        kafkaProducer.notify(newVitalsRangesMessage, settings.KAFKA_TOPIC_DEVICE(), serialNumber, null);

        handleOngoingPmEncounters(patientAlreadyInUse ? null : patient != null ? patient : ongoingEncounter);
    }

    public SdcRemoteDevice getSdcRemoteDevice() throws ActionOnDisconnectedPatientMonitor {
        if (isConnected()) {
            return sdcRemoteDevice;
        }
        throw new ActionOnDisconnectedPatientMonitor(
                "Cannot obtain remote device on a disconnected patient monitor %s.".formatted(this));
    }

    public MdibAccess getMdibAccess() throws ActionOnDisconnectedPatientMonitor {
        return getSdcRemoteDevice().getMdibAccess();
    }

    public String getPatientId() throws ActionOnDisconnectedPatientMonitor {
        var payload = getPatient();
        return payload != null ? payload.getPrimaryIdentifier() : null;
    }

    public PatientPayload getPatient() throws ActionOnDisconnectedPatientMonitor {
        patientLock.lock();
        try {
            return validatedPatient;
        } finally {
            patientLock.unlock();
        }
    }

    public List<VitalsRangePayload> getVitalsRangePayloads() throws ActionOnDisconnectedPatientMonitor {
        var patientId = getPatientId();
        var mdibAccess = getMdibAccess();
        return getLimitAlertConditions(mdibAccess).stream()
                .map(state -> {
                    try {
                        var vitalsRangePayload = processorFactory
                                .createVitalRangeProcessor(mdibAccess, state)
                                .getVitalsRangePayload();
                        if (vitalsCache.hasChanged(patientId, vitalsRangePayload.getCode(), vitalsRangePayload)) {
                            vitalsCache.addOrUpdate(patientId, vitalsRangePayload.getCode(), vitalsRangePayload);
                            return vitalsRangePayload;
                        }
                    } catch (ProcessingError e) {
                        LOG.warn("Error processing vital ranges on discovered device: {}", getDeviceEpr(), e);
                    }
                    return null;
                })
                .filter(Objects::nonNull)
                .toList();
    }

    public void startListeningEvents() throws ActionOnDisconnectedPatientMonitor {
        if (serialNumber != null) {
            if (consumerReportProcessor != null) {
                sdcRemoteDevice.getMdibAccessObservable().unregisterObserver(consumerReportProcessor);
            }

            consumerReportProcessor = consumerReportProcessorFactory.create(serialNumber);
            sdcRemoteDevice.getMdibAccessObservable().registerObserver(consumerReportProcessor);
        } else {
            throw new ActionOnDisconnectedPatientMonitor(
                    "Attempting for listen to events of a patient monitor with no serial number");
        }
    }

    public ConfigPayload getConfigPayload() throws ActionOnDisconnectedPatientMonitor {
        var audioEnabled = true;
        var audioPauseEnabled = false;

        var alertSystemDescriptor = getMdibAccess().findEntitiesByType(AlertSystemDescriptor.class).stream()
                .filter(entity -> Objects.equals(entity.getParent().orElse(null), entity.getParentMds()))
                .findFirst()
                .orElse(null);
        if (alertSystemDescriptor != null) {
            var alertSystemState =
                    alertSystemDescriptor.getFirstState(AlertSystemState.class).orElse(null);
            if (alertSystemState != null) {
                var alertSystemAudioActivation = alertSystemState.getSystemSignalActivation().stream()
                        .filter(activation -> activation.getManifestation() == AlertSignalManifestation.AUD)
                        .findFirst()
                        .orElse(null);
                if (alertSystemAudioActivation != null) {
                    audioEnabled = alertSystemAudioActivation.getState() != AlertActivation.OFF;
                    audioPauseEnabled = alertSystemAudioActivation.getState() == AlertActivation.PSD;
                }
            }
        }

        return new ConfigPayload(audioEnabled, audioPauseEnabled);
    }

    public void handlePatientChange(PatientPayload newPatient, PatientPayload oldPatient) {
        try {
            if (newPatient == null || newPatient.isEmpty() && newPatient.getAssociation() != ContextAssociation.PRE) {
                handleSessionClosed(oldPatient);
            } else if (newPatient.getAssociation() == ContextAssociation.ASSOC
                    && newPatient.hasValidators(settings.PATIENT_MONITOR_VALIDATOR_ID())) {
                var patientAlreadyInUse = checkPatientAlreadyInUse(newPatient);
                if (!patientAlreadyInUse) {
                    handleSessionStarted(newPatient);
                }
            } else if (newPatient.getAssociation() == ContextAssociation.PRE
                    && !newPatient.hasValidators(settings.CENTRAL_HUB_VALIDATOR_ID())) {
                handleEhrSearch(newPatient);
            } else if (newPatient.getAssociation() == ContextAssociation.NO
                    && newPatient.hasValidators(settings.CENTRAL_HUB_VALIDATOR_ID())) {
                handlePatientRejected(newPatient);
            } else {
                LOG.info(
                        "[{}] New unknown patient context state with association {} and validators {} detected. Ignoring.",
                        this,
                        newPatient.getAssociation(),
                        newPatient.getValidators());
            }
        } catch (ProcessingError e) {
            LOG.error("[{}] Error processing patient context, device disconnected", this, e);
        }
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("serialNumber", serialNumber)
                .toString();
    }

    private boolean checkPatientAlreadyInUse(PatientPayload patient) {
        if (patient == null || patient.isEmpty()) {
            return false;
        }
        var patientId = patient.getPrimaryIdentifier();
        var sharedPatientIdKey = getSharedPatientIdKey(patientId);
        var claimingPatient = redis.set(
                sharedPatientIdKey,
                serialNumber,
                SetArgs.Builder.ex(settings.PATIENT_CLAIM_EXPIRATION()).nx());
        var patientOwner = redis.get(sharedPatientIdKey);

        var patientAlreadyInUse = !Objects.equals(claimingPatient, "OK") && !Objects.equals(patientOwner, serialNumber);
        if (patientAlreadyInUse) {
            LOG.info("[{}] Patient admission rejected. Patient {} already monitored.", this, patientId);
            setPatientContextSco(SetPatientContextParams.fromPatientPayload(patient, ContextAssociation.NO));
        }
        return patientAlreadyInUse;
    }

    private PatientPayload handleOngoingCentralHubEncounters(boolean patientAlreadyInUse)
            throws ActionOnDisconnectedPatientMonitor {
        if (serialNumber == null) {
            throw new ActionOnDisconnectedPatientMonitor(
                    "Attempting to get encounters of a patient monitor with no serial number");
        }

        try {
            var encounter = deviceApi.getDeviceEncounter(serialNumber);

            if (encounter != null && encounter.status().equals(EncounterStatus.PLANNED.getValue())) {
                var patientPayload = getNonValidatedPatient();
                if (patientPayload == null
                        || patientPayload.isEmpty()
                        || patientPayload.getAssociation() == ContextAssociation.PRE
                        || patientPayload.getAssociation() == ContextAssociation.NO
                                && !Objects.equals(
                                        patientPayload.getPrimaryIdentifier(),
                                        encounter.subject().primaryIdentifier())
                        || patientAlreadyInUse) {
                    var params = SetPatientContextParams.fromApiPatient(encounter.subject());
                    setPatientContextSco(params);
                }

                return PatientPayload.fromApiPatient(encounter.subject(), Set.of(settings.CENTRAL_HUB_VALIDATOR_ID()));
            }
        } catch (ApiRequestException e) {
            LOG.warn("[{}] Failed to obtain encounters from device service.", this, e);
        }
        return null;
    }

    private void handleOngoingPmEncounters(PatientPayload patient) throws ActionOnDisconnectedPatientMonitor {
        handlePatientChange(patient, null);
    }

    private void setPatientContextSco(SetPatientContextParams params) {
        try {
            if (setPatientContextScoOperation.isEnabledFor(this)) {
                setPatientContextScoOperation.run(this, params);
            } else {
                LOG.warn("[{}] Set patient context SCO not enable for PM.", this);
            }
        } catch (ScoOperationException e) {
            LOG.warn("[{}] Failed to send patient context to PM.", this, e);
        }
    }

    private List<AlertPayload> getAlertPayloads(String patientId, AlertConditionKind alertKind)
            throws ActionOnDisconnectedPatientMonitor {
        var mdibAccess = getMdibAccess();
        var alertSignalStates = getAlerts(mdibAccess, alertKind);

        List<AlertPayload> alerts;
        if (alertSignalStates != null) {
            alerts = alertSignalStates.stream()
                    .map(alertSignalState -> {
                        try {
                            var processor = processorFactory.createAlertChangeProcessor(
                                    mdibAccess, alertSignalState, serialNumber, SensorType.PM.code, patientId);
                            var alertPayload = processor.getAlertSignalPayload();
                            var alertKey = processor.getCacheKey();
                            if (alertsCache.hasChanged(patientId, alertKey, alertPayload)) {
                                return alertPayload;
                            }
                        } catch (ProcessingError error) {
                            LOG.warn("Error processing alert", error);
                        }
                        return null;
                    })
                    .filter(Objects::nonNull)
                    .toList();
        } else {
            alerts = List.of();
        }
        return alerts;
    }

    private List<SensorPayload> getConnectedSensorsPayloads() throws ActionOnDisconnectedPatientMonitor {
        return getConnectedSensors(getMdibAccess()).stream()
                .map(descriptor -> {
                    var devicePrimaryIdentifier =
                            getValueFromProductionSpec(descriptor, ProductionSpecCodes.DEVICE_PRIMARY_IDENTIFIER);
                    var deviceTypeCode = getValueFromProductionSpec(descriptor, ProductionSpecCodes.DEVICE_CODE);
                    return new SensorPayload(devicePrimaryIdentifier, deviceTypeCode, deviceTypeCode);
                })
                .toList();
    }

    private PatientPayload getNonValidatedPatient() throws ActionOnDisconnectedPatientMonitor {
        PatientPayload result = null;

        var patientContext = getPatientContextState(getMdibAccess());
        var processor = processorFactory.createPatientContextProcessor(patientContext);

        if (patientContext != null) {
            try {
                result = processor.getPatientPayload();
            } catch (ProcessingError e) {
                LOG.error("[{}] Error processing patient information.", this, e);
            }
        }

        return result;
    }

    private void handleSessionClosed(PatientPayload oldPatient) throws ProcessingError {
        LOG.info("[{}] Empty or null patient context detected. Closing session.", this);
        var patientPrimaryIdentifier =
                oldPatient != null && !oldPatient.isEmpty() ? oldPatient.getPrimaryIdentifier() : null;

        var message = new PatientSessionClosedBrokerMessage(
                uuidProvider.get(),
                instantProvider.now(),
                new PatientSessionClosedPayload(patientPrimaryIdentifier, getSerialNumber()));
        kafkaProducer.notify(message, settings.KAFKA_TOPIC_DEVICE(), serialNumber, null);

        setValidatedPatient(null);
    }

    private void handleSessionStarted(PatientPayload patient) {
        LOG.info("[{}] New validated patient context detected. Starting session.", this);

        var message = new PatientSessionStartedBrokerMessage(
                uuidProvider.get(),
                instantProvider.now(),
                new PatientSessionStartedPayload(getSerialNumber(), patient));
        kafkaProducer.notify(message, settings.KAFKA_TOPIC_DEVICE(), getSerialNumber(), null);

        setValidatedPatient(patient);
    }

    private void handleEhrSearch(PatientPayload patient) {
        LOG.info("[{}] New pre-associated patient context detected. Starting EHR search.", this);

        Collection<EhrPatient> patients;
        try {
            patients = ehrApi.searchPatients(EhrSearchCriteria.fromPatientPayload(patient));
        } catch (ApiRequestException e) {
            LOG.warn("Error searching EHR patients.", e);
            patients = List.of();
        }

        SetPatientContextParams scoParams;
        if (patients.isEmpty()) {
            scoParams = SetPatientContextParams.fromPatientPayload(PatientPayload.createEmpty(ContextAssociation.NO));
        } else {
            scoParams = new SetPatientContextParams(patients.stream()
                    .map(ehrPatient -> {
                        var association = ContextAssociation.PRE;
                        var patientIdentifier = ehrPatient.patientIdentifiers().stream()
                                .findFirst()
                                .orElse(null);
                        if (patientIdentifier != null && !patientIdentifier.isBlank()) {
                            var patientOwner = redis.get(getSharedPatientIdKey(patientIdentifier));
                            if (patientOwner != null && !patientOwner.isBlank()) {
                                association = ContextAssociation.NO;
                            }
                        }
                        return SetPatientContextParams.Patient.fromEhrPatient(ehrPatient, association);
                    })
                    .toList());
        }

        try {
            if (setPatientContextScoOperation.isEnabledFor(this)) {
                setPatientContextScoOperation.run(this, scoParams);
            } else {
                LOG.warn("[{}] Failed to send EHR response to PM. Set patient SCO not enabled for PM.", this);
            }
        } catch (ScoOperationException e) {
            LOG.error("[{}] Failed to send EHR response to PM.", this, e);
        }
    }

    private void handlePatientRejected(PatientPayload patient) {
        LOG.info("[{}] New patient context not associated detected detected. Rejecting patient admission.", this);

        var payload = new PatientAdmissionRejectedPayload(getSerialNumber(), patient.getPrimaryIdentifier());
        var message = new PatientAdmissionRejectedBrokerMessage(uuidProvider.get(), instantProvider.now(), payload);
        kafkaProducer.notify(message, settings.KAFKA_TOPIC_DEVICE(), serialNumber, null);
    }

    private void setValidatedPatient(PatientPayload validatedPatient) {
        patientLock.lock();
        try {
            this.validatedPatient = validatedPatient;
        } finally {
            patientLock.unlock();
        }
    }
}
