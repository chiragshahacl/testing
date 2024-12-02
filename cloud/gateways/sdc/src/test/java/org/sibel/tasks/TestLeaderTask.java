package org.sibel.tasks;

import static org.mockito.Mockito.*;
import static org.sibel.constants.RedisKeys.*;

import com.google.gson.Gson;
import io.lettuce.core.api.sync.RedisCommands;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.sibel.config.Settings;
import org.somda.sdc.dpws.client.Client;
import org.somda.sdc.dpws.client.DiscoveredDevice;
import org.somda.sdc.dpws.client.event.ProbedDeviceFoundMessage;

class TestLeaderTask {
    private static final String DEVICE_EPR = "device epr";
    private static final int MAX_FOLLOWERS = 5;
    private static final String FOLLOWER_ID_1 = "follower 1";
    private static final String FOLLOWER_ID_2 = "follower 2";

    private final DiscoveredDevice discoveredDevice =
            new DiscoveredDevice(DEVICE_EPR, List.of(), List.of(), List.of(), 0);
    private final String discoveredDeviceAsJson = "discovered device as json";
    private final ProbedDeviceFoundMessage probedDeviceFoundMessage =
            new ProbedDeviceFoundMessage(discoveredDevice, "some id");

    private final Client clientMock = mock();
    private final Settings settingsMock = mock();
    private final RedisCommands<String, String> syncMock = mock();
    private final Gson gsonMock = mock();

    private final LeaderTask leaderTask = new LeaderTask(clientMock, settingsMock, syncMock, gsonMock);

    @BeforeEach
    void setup() {
        reset(clientMock, settingsMock, syncMock, gsonMock);
        configureSyncMock();
        configureGsonMock();
        configureSettings();
    }

    @Test
    void testDiscoveredDeviceShouldBeAssignedToFollowerWithTheLeastAmount() {
        when(syncMock.scard(getFollowerDevicesKey(FOLLOWER_ID_1))).thenReturn(3L);
        when(syncMock.scard(getFollowerDevicesKey(FOLLOWER_ID_2))).thenReturn(1L);

        leaderTask.handleProbeDeviceFound(probedDeviceFoundMessage);

        // Verify device deleted from follower devices
        verify(syncMock).srem(getFollowerDevicesKey(FOLLOWER_ID_1), DEVICE_EPR);
        verify(syncMock).srem(getFollowerDevicesKey(FOLLOWER_ID_2), DEVICE_EPR);

        // Assign to the follower with the least amount of followers
        verify(syncMock).publish(getFollowerChannelKey(FOLLOWER_ID_2), discoveredDeviceAsJson);
        verify(syncMock).sadd(getFollowerChannelKey(FOLLOWER_ID_2), DEVICE_EPR);
    }

    @Test
    void testDiscoverDeviceAlreadyClaimedShouldNotBeAssigned() {
        when(syncMock.scard(getFollowerDevicesKey(FOLLOWER_ID_1))).thenReturn(3L);
        when(syncMock.scard(getFollowerDevicesKey(FOLLOWER_ID_2))).thenReturn(1L);

        when(syncMock.get(getDeviceKey(DEVICE_EPR))).thenReturn(FOLLOWER_ID_1);

        leaderTask.handleProbeDeviceFound(probedDeviceFoundMessage);

        // Added to the device list of the correct follower
        verify(syncMock).sadd(getFollowerDevicesKey(FOLLOWER_ID_1), DEVICE_EPR);

        // Not assigned
        verify(syncMock, never()).publish(any(), eq(discoveredDeviceAsJson));
        verify(syncMock, never()).sadd(getFollowerChannelKey(FOLLOWER_ID_2), DEVICE_EPR);
    }

    @Test
    void testDiscoveredDeviceShouldNotBeAssignedToMaxedOutFollowers() {
        when(syncMock.scard(getFollowerDevicesKey(FOLLOWER_ID_1))).thenReturn((long) MAX_FOLLOWERS);
        when(syncMock.scard(getFollowerDevicesKey(FOLLOWER_ID_2))).thenReturn((long) MAX_FOLLOWERS);

        leaderTask.handleProbeDeviceFound(probedDeviceFoundMessage);

        // Verify device deleted from follower devices
        verify(syncMock).srem(getFollowerDevicesKey(FOLLOWER_ID_1), DEVICE_EPR);
        verify(syncMock).srem(getFollowerDevicesKey(FOLLOWER_ID_2), DEVICE_EPR);

        // Not assigned
        verify(syncMock, never()).publish(any(), eq(discoveredDeviceAsJson));
        verify(syncMock, never()).sadd(any(), eq(DEVICE_EPR));
    }

    private void configureSyncMock() {
        when(syncMock.keys(getFollowerClaimKey("*")))
                .thenReturn(List.of(getFollowerClaimKey(FOLLOWER_ID_1), getFollowerClaimKey(FOLLOWER_ID_2)));
    }

    private void configureGsonMock() {
        when(gsonMock.toJson(discoveredDevice)).thenReturn(discoveredDeviceAsJson);
    }

    private void configureSettings() {
        when(settingsMock.FOLLOWER_MAX_CONNECTED_DEVICES()).thenReturn(MAX_FOLLOWERS);
    }
}
