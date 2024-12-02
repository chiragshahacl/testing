package org.sibel.tasks;

import static org.sibel.constants.RedisKeys.*;

import com.google.inject.Inject;
import com.google.inject.assistedinject.Assisted;
import com.google.inject.name.Named;
import io.lettuce.core.SetArgs;
import io.lettuce.core.api.sync.RedisCommands;
import java.time.Duration;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.PatientMonitor;
import org.sibel.config.Settings;
import org.sibel.constants.DI;
import org.sibel.exceptions.ActionOnDisconnectedPatientMonitor;
import org.sibel.exceptions.FailedToDisconnectPatientMonitor;
import org.sibel.factories.InstantProvider;
import org.sibel.factories.UuidProvider;
import org.sibel.models.RealtimeStateBrokerMessage;
import org.sibel.models.payloads.RealtimeStatePayload;
import org.sibel.producers.KafkaMessageProducer;
import org.sibel.repositories.PatientMonitorRepository;

// TODO: Modify to run on a single thread (i.e. only one task for all devices)
public class DeviceConnectionCheckTask implements Runnable {
    private static final Logger LOG = LogManager.getLogger(DeviceConnectionCheckTask.class);

    private final PatientMonitor patientMonitor;
    private final RedisCommands<String, String> sync;
    private final String consumerId;
    private final KafkaMessageProducer kafkaProducer;
    private final UuidProvider uuidProvider;
    private final InstantProvider instantProvider;

    private final Integer MESSAGE_INTERVAL_MS;
    private final String MESSAGE_BROKER_SDC_REALTIME_STATE_TOPIC;
    private final Duration REFRESH_CLAIM_INTERVAL;

    private boolean running = false;

    @Inject
    public DeviceConnectionCheckTask(
            @Assisted String serialNumber,
            RedisCommands<String, String> sync,
            @Named(DI.CONSUMER_ID) String consumerId,
            Settings settings,
            KafkaMessageProducer kafkaProducer,
            PatientMonitorRepository patientMonitorRepository,
            UuidProvider uuidProvider,
            InstantProvider instantProvider) {
        this.uuidProvider = uuidProvider;
        this.instantProvider = instantProvider;
        this.patientMonitor = patientMonitorRepository.getBySerialNumber(serialNumber);
        this.sync = sync;
        this.consumerId = consumerId;

        // Initialize constants
        MESSAGE_INTERVAL_MS = settings.REALTIME_STATE_MESSAGE_DURATION() * 1000;
        MESSAGE_BROKER_SDC_REALTIME_STATE_TOPIC = settings.KAFKA_TOPIC_SDC_REALTIME_STATE();
        REFRESH_CLAIM_INTERVAL = Duration.ofSeconds(settings.CLAIM_INTERVAL());

        // Initialize Kafka producer
        this.kafkaProducer = kafkaProducer;
    }

    @Override
    public void run() {
        LOG.info("Start device connection health check: %s".formatted(patientMonitor.getSerialNumber()));
        running = true;
        while (running) {
            try {
                refreshClaim();
                var statePayload = new RealtimeStatePayload(patientMonitor.getSerialNumber(), running);
                var realtimeStateBrokerMessage =
                        new RealtimeStateBrokerMessage(uuidProvider.get(), instantProvider.now(), statePayload);
                kafkaProducer.notify(
                        realtimeStateBrokerMessage,
                        MESSAGE_BROKER_SDC_REALTIME_STATE_TOPIC,
                        patientMonitor.getSerialNumber(),
                        null);

                //noinspection BusyWait
                Thread.sleep(MESSAGE_INTERVAL_MS);

                setRunning(patientMonitor.isConnected());
            } catch (Exception e) {
                LOG.error("Error running device connection health check.", e);
                running = false;
            }
        }

        try {
            patientMonitor.disconnect();
            // TODO: Remove Patient monitor from repository
        } catch (FailedToDisconnectPatientMonitor e) {
            // We ignore this error as the patient monitor is disconnected, it is bound to raise an error.
            // But we run it anyway to clean up any running task or callback.
            LOG.debug("[{}] Failed to force disconnect.", patientMonitor, e);
        } finally {
            freeClaims();
        }
    }

    public void stop() {
        setRunning(false);
    }

    public synchronized boolean isRunning() {
        return running;
    }

    private synchronized void setRunning(boolean running) {
        this.running = running;
    }

    private void refreshClaim() {
        sync.set(getDeviceKey(patientMonitor.getDeviceEpr()), consumerId, SetArgs.Builder.ex(REFRESH_CLAIM_INTERVAL));
        sync.set(
                getDevicePrimaryIdentifierKey(patientMonitor.getSerialNumber()),
                consumerId,
                SetArgs.Builder.ex(REFRESH_CLAIM_INTERVAL));
        try {
            var patientId = patientMonitor.getPatientId();
            if (patientId != null) {
                sync.set(
                        getSharedPatientIdKey(patientId),
                        patientMonitor.getSerialNumber(),
                        SetArgs.Builder.ex(REFRESH_CLAIM_INTERVAL));
            }
        } catch (ActionOnDisconnectedPatientMonitor e) {
            LOG.debug("[{}] Failed to refresh monitored patient id.", patientMonitor, e);
        }
        LOG.debug("[{}] Refreshed the claim monitoring of device", patientMonitor);
    }

    private void freeClaims() {
        sync.del(getDeviceKey(patientMonitor.getDeviceEpr()));
        sync.del(getDevicePrimaryIdentifierKey(patientMonitor.getSerialNumber()));
        LOG.debug("[{}] Freeing claims.", patientMonitor);
    }
}
