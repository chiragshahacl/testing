package org.sibel.tasks;

import static org.sibel.constants.RedisKeys.*;

import com.google.common.eventbus.Subscribe;
import com.google.gson.Gson;
import com.google.gson.JsonParseException;
import com.google.inject.Inject;
import com.google.inject.name.Named;
import io.lettuce.core.SetArgs;
import io.lettuce.core.pubsub.RedisPubSubAdapter;
import io.lettuce.core.pubsub.RedisPubSubListener;
import java.util.*;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.PatientMonitor;
import org.sibel.config.Settings;
import org.sibel.constants.DI;
import org.sibel.exceptions.*;
import org.sibel.factories.PatientMonitorFactory;
import org.sibel.factories.TaskFactory;
import org.sibel.repositories.PatientMonitorRepository;
import org.sibel.utils.CacheClient;
import org.somda.sdc.dpws.client.DiscoveredDevice;
import org.somda.sdc.glue.consumer.WatchdogObserver;
import org.somda.sdc.glue.consumer.event.WatchdogMessage;

public class FollowerTask implements Callable<Integer> {
    private static final Logger LOG = LogManager.getLogger();
    private final String consumerId;
    private final CacheClient cacheClient;
    private final TaskFactory taskFactory;
    private final ExecutorService executor;
    private final Settings settings;
    private final PatientMonitorFactory patientMonitorFactory;
    private final PatientMonitorRepository patientMonitorRepository;

    private final RedisPubSubListener<String, String> listener;
    private boolean running;

    record ConnectedDeviceRunningTasks(DeviceConnectionCheckTask healthCheck, PatientMonitor patientMonitor) {}

    private final ArrayList<ConnectedDeviceRunningTasks> runningTasksList = new ArrayList<>();

    @Inject
    public FollowerTask(
            @Named(DI.CONSUMER_ID) String consumerId,
            CacheClient cacheClient,
            TaskFactory taskFactory,
            ExecutorService executor,
            Settings settings,
            Gson gson,
            PatientMonitorFactory patientMonitorFactory,
            PatientMonitorRepository patientMonitorRepository) {
        this.consumerId = consumerId;
        this.cacheClient = cacheClient;
        this.executor = executor;
        this.settings = settings;
        this.taskFactory = taskFactory;
        this.patientMonitorFactory = patientMonitorFactory;
        this.patientMonitorRepository = patientMonitorRepository;

        listener = new RedisPubSubAdapter<>() {
            @Override
            public void message(String channel, String message) {
                try {
                    var discoveredDevice = gson.fromJson(message, DiscoveredDevice.class);
                    handleDiscoveredDevice(discoveredDevice);
                } catch (JsonParseException e) {
                    LOG.warn("Error parsing discovered device", e);
                } catch (Exception e) {
                    LOG.error("Error discovering device", e);
                }
            }
        };
    }

    @Override
    public Integer call() {
        running = true;
        cacheClient.registerPubSubListener(getFollowerChannelKey(consumerId), listener);
        LOG.info("Follower task started.");
        while (running) {
            try {
                cleanUpRunningTasks(false);
                Thread.sleep(30000); // 30s
            } catch (InterruptedException e) {
                running = false;
                LOG.error("Follower task interrupted.");
                throw new RuntimeException(e);
            }
        }
        return 0;
    }

    public void stop() {
        if (running) {
            try {
                cacheClient.unregisterPubSubListener(getFollowerChannelKey(consumerId), listener);
                cleanUpRunningTasks(true);
            } catch (Exception e) {
                LOG.warn("Failed to clean up follower task", e);
            }

            running = false;
            LOG.info("Follower task stopped.");
        }
    }

    public boolean isRunning() {
        return running;
    }

    public void handleDiscoveredDevice(DiscoveredDevice discoveredDevice) {
        var sync = cacheClient.getRedisCommands();

        var deviceEpr = discoveredDevice.getEprAddress();
        LOG.info("Found device with epr {}.", deviceEpr);

        var claimingDevice = sync.set(
                getDeviceKey(deviceEpr),
                consumerId,
                SetArgs.Builder.ex(settings.CLAIM_INTERVAL()).nx());

        if (Objects.equals(claimingDevice, "OK")) {
            LOG.info("Claimed monitoring of device {}.", deviceEpr);
            sync.sadd(getFollowerDevicesKey(consumerId), deviceEpr);

            var watchdogObserver = new WatchdogObserver() {
                @Subscribe
                public void onWatchdogTriggered(WatchdogMessage message) {
                    LOG.info("Executing watchdog for device {}.", deviceEpr);
                    sync.del(getDeviceKey(deviceEpr));
                    sync.srem(getFollowerDevicesKey(consumerId), deviceEpr);
                }
            };
            var patientMonitor = patientMonitorFactory.create(discoveredDevice, watchdogObserver);
            try {
                patientMonitor.connect();
            } catch (FailedToConnectPatientMonitor error) {
                LOG.error("Error connecting to device {}. Forcing disconnect.", deviceEpr, error);
            }

            var serialNumber = patientMonitor.getSerialNumber();
            if (!patientMonitor.isConnected()
                    || serialNumber == null
                    || serialNumber.isEmpty()
                    || serialNumber.equals("-")) {
                if (patientMonitor.isConnected()) {
                    LOG.warn(
                            "PM with invalid serial number connected {}, disconnecting device {}.",
                            serialNumber,
                            deviceEpr);
                }
                try {
                    patientMonitor.disconnect();
                } catch (FailedToDisconnectPatientMonitor e) {
                    LOG.warn("Error disconnecting device {}.", deviceEpr, e);
                } finally {
                    sync.del(getDeviceKey(deviceEpr));
                    sync.srem(getFollowerDevicesKey(consumerId), deviceEpr);
                }
            } else {
                try {
                    // Update once the serial number for the patient monitor is added
                    LOG.info("Patient monitor connected: {}.", serialNumber);

                    patientMonitor.notifyDiscovery();
                    patientMonitorRepository.add(patientMonitor);

                    patientMonitor.startListeningEvents();

                    // TODO: This should run separately, not one task per PM
                    var connectionCheckProcessor = taskFactory.createDeviceConnectionCheckTask(serialNumber);
                    executor.submit(connectionCheckProcessor);
                    runningTasksList.add(new ConnectedDeviceRunningTasks(connectionCheckProcessor, patientMonitor));
                } catch (ActionOnDisconnectedPatientMonitor e) {
                    LOG.error("Error connecting device with epr {}.", deviceEpr, e);
                    sync.del(getDeviceKey(deviceEpr));
                    sync.srem(getFollowerDevicesKey(consumerId), deviceEpr);
                }
            }
        } else {
            LOG.info("Ignoring already monitored device with epr {}.", deviceEpr);
        }
    }

    private synchronized void cleanUpRunningTasks(boolean forceClose) {
        var iterator = runningTasksList.iterator();
        while (iterator.hasNext()) {
            var runningTasks = iterator.next();
            if (forceClose || !runningTasks.healthCheck.isRunning()) {
                runningTasks.healthCheck.stop();
                iterator.remove();
            }
        }
    }
}
