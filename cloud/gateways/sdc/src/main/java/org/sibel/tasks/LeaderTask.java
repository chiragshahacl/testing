package org.sibel.tasks;

import static org.sibel.constants.RedisKeys.*;

import com.google.common.eventbus.Subscribe;
import com.google.gson.Gson;
import com.google.inject.Inject;
import com.google.inject.name.Named;
import io.lettuce.core.api.sync.RedisCommands;
import java.time.Duration;
import java.util.concurrent.Callable;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.config.Settings;
import org.sibel.constants.DI;
import org.somda.sdc.dpws.client.Client;
import org.somda.sdc.dpws.client.DiscoveryObserver;
import org.somda.sdc.dpws.client.event.ProbedDeviceFoundMessage;
import org.somda.sdc.dpws.soap.exception.TransportException;
import org.somda.sdc.dpws.soap.interception.InterceptorException;
import org.somda.sdc.glue.consumer.SdcDiscoveryFilterBuilder;

public class LeaderTask implements Callable<Integer> {
    private static final Logger LOG = LogManager.getLogger();

    private boolean running = false;

    Client client;
    private final Settings settings;
    private final RedisCommands<String, String> sync;
    private final Gson gson;
    private final DiscoveryObserver discoveryObserver;

    @Inject
    public LeaderTask(
            @Named(DI.CLIENT) Client client, Settings settings, RedisCommands<String, String> sync, Gson gson) {
        this.client = client;
        this.settings = settings;
        this.sync = sync;
        this.gson = gson;

        discoveryObserver = new DiscoveryObserver() {
            @Subscribe
            void deviceFound(ProbedDeviceFoundMessage message) {
                handleProbeDeviceFound(message);
            }
        };
    }

    @Override
    public Integer call() {
        running = true;

        client.registerDiscoveryObserver(discoveryObserver);
        LOG.info("Leader task started.");

        var discoveryFilterBuilder = SdcDiscoveryFilterBuilder.create();
        var discoveryFilter = discoveryFilterBuilder.get();
        while (running) {
            // filter discovery for SDC devices only
            LOG.info("Starting discovery...");
            try {
                client.probe(discoveryFilter);
                Thread.sleep(Duration.ofSeconds(settings.PROBE_INTERVAL()));
            } catch (TransportException | InterceptorException | InterruptedException e) {
                running = false;
                throw new RuntimeException(e);
            }
        }
        client.unregisterDiscoveryObserver(discoveryObserver);
        LOG.info("Leader task stopped.");
        return 0;
    }

    public boolean isRunning() {
        return running;
    }

    public void stop() {
        running = false;
    }

    public void handleProbeDeviceFound(ProbedDeviceFoundMessage message) {
        var discoveredDevice = message.getPayload();

        var ownerFollowerId = sync.get(getDeviceKey(discoveredDevice.getEprAddress()));
        var claimed = ownerFollowerId != null && !ownerFollowerId.isEmpty();
        if (!claimed) {
            var minCount = settings.FOLLOWER_MAX_CONNECTED_DEVICES();
            String assignedFollower = null;
            for (var followerKey : sync.keys(getFollowerClaimKey("*"))) {
                var followerId = getFollowerIdFromClaimKey(followerKey);
                var followerDevicesKey = getFollowerDevicesKey(followerId);

                sync.srem(followerDevicesKey, discoveredDevice.getEprAddress());

                int deviceCount = Math.toIntExact(sync.scard(followerDevicesKey));
                if (deviceCount < settings.FOLLOWER_MAX_CONNECTED_DEVICES() && deviceCount < minCount) {
                    minCount = deviceCount;
                    assignedFollower = followerId;
                }
            }

            if (assignedFollower != null) {
                LOG.info(
                        "Assigning discovered device with EPR address {} to follower {}",
                        discoveredDevice.getEprAddress(),
                        assignedFollower);
                var jsonDiscoveredMessage = gson.toJson(discoveredDevice);
                sync.sadd(getFollowerDevicesKey(assignedFollower), discoveredDevice.getEprAddress());
                sync.publish(getFollowerChannelKey(assignedFollower), jsonDiscoveredMessage);
            } else {
                LOG.warn(
                        "There are no free SDC followers to send newly discovered device {}",
                        discoveredDevice.getEprAddress());
            }
        } else {
            sync.sadd(getFollowerDevicesKey(ownerFollowerId), discoveredDevice.getEprAddress());
            LOG.info(
                    "Device with epr {} already monitored by follower {}",
                    discoveredDevice.getEprAddress(),
                    ownerFollowerId);
        }
    }
}
