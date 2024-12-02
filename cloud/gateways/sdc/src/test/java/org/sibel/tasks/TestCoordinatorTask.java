package org.sibel.tasks;

import static org.mockito.Mockito.*;
import static org.sibel.constants.RedisKeys.*;

import io.lettuce.core.api.sync.RedisCommands;
import java.util.concurrent.ExecutorService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.sibel.config.Settings;
import org.sibel.constants.ServerRole;

class TestCoordinatorTask {
    private static final String CONSUMER_ID = "current consumer id";
    private static final String ANOTHER_CONSUMER_ID = "another consumer id";

    // Mocks
    private final LeaderTask leaderTaskMock = mock();
    private final FollowerTask followerTaskMock = mock();
    private final KafkaConsumerTask kafkaConsumerTaskMock = mock();
    private final RedisCommands<String, String> syncMock = mock();
    private final ExecutorService executorMock = mock();
    private final Settings settingsMock = mock();

    private final CoordinatorTaskImpl coordinator = new CoordinatorTaskImpl(
            CONSUMER_ID, leaderTaskMock, followerTaskMock, kafkaConsumerTaskMock, syncMock, executorMock, settingsMock);

    @BeforeEach
    void setup() {
        reset(leaderTaskMock, followerTaskMock, syncMock, executorMock, settingsMock);

        configureSettingsMock();
    }

    @Test
    void testNoLeaderShouldStartAsLeader() {
        when(syncMock.set(eq(LEADER_KEY), eq(CONSUMER_ID), any())).thenReturn("OK");

        coordinator.spawnTasks();

        // Firstly claims leadership, secondly refreshes leader claim
        verify(syncMock, times(2)).set(eq(LEADER_KEY), eq(CONSUMER_ID), any());

        verify(followerTaskMock).stop();
        verify(executorMock).submit(leaderTaskMock);
    }

    @Test
    void testLeaderClaimedShouldStartAsFollower() {
        when(syncMock.get(LEADER_KEY)).thenReturn(ANOTHER_CONSUMER_ID);

        coordinator.spawnTasks();

        // Try claims leadership
        verify(syncMock).set(eq(LEADER_KEY), eq(CONSUMER_ID), any());
        // Refresh follower claim
        verify(syncMock).set(eq(getFollowerClaimKey(CONSUMER_ID)), anyString(), any());
        verify(syncMock).expire(eq(getFollowerClaimKey(CONSUMER_ID)), any());
        verify(syncMock).expire(eq(getFollowerDevicesKey(CONSUMER_ID)), any());

        verify(leaderTaskMock).stop();
        verify(executorMock).submit(followerTaskMock);
    }

    @Test
    void testAlreadyLeaderShouldRefreshClaim() {
        when(syncMock.get(LEADER_KEY)).thenReturn(CONSUMER_ID);

        coordinator.spawnTasks();

        // Firstly claims leadership, secondly refreshes claim
        verify(syncMock, times(2)).set(eq(LEADER_KEY), eq(CONSUMER_ID), any());

        verify(followerTaskMock).stop();
        verify(executorMock).submit(leaderTaskMock);
    }

    @Test
    void testSingleInstanceModeShouldStartBothLeaderAndFollower() {
        when(settingsMock.SINGLE_INSTANCE_MODE()).thenReturn(true);

        when(syncMock.set(eq(LEADER_KEY), eq(CONSUMER_ID), any())).thenReturn("OK");

        coordinator.spawnTasks();

        // Firstly claims leadership, secondly refreshes leader claim
        verify(syncMock, times(2)).set(eq(LEADER_KEY), eq(CONSUMER_ID), any());
        // Refresh follower claim
        verify(syncMock).set(eq(getFollowerClaimKey(CONSUMER_ID)), anyString(), any());
        verify(syncMock).expire(eq(getFollowerClaimKey(CONSUMER_ID)), any());
        verify(syncMock).expire(eq(getFollowerDevicesKey(CONSUMER_ID)), any());

        verify(executorMock).submit(leaderTaskMock);
        verify(executorMock).submit(followerTaskMock);
    }

    @Test
    void testLeaderClaimedButForcedLeaderRoleShouldStartAsLeader() {
        when(syncMock.get(LEADER_KEY)).thenReturn(ANOTHER_CONSUMER_ID);
        when(settingsMock.COORDINATOR_SERVER_ROLE()).thenReturn(ServerRole.LEADER);

        coordinator.spawnTasks();

        // Refresh leader claim
        verify(syncMock).set(eq(LEADER_KEY), eq(CONSUMER_ID), any());

        verify(followerTaskMock).stop();
        verify(executorMock).submit(leaderTaskMock);
    }

    @Test
    void testNoLeaderButForcedFollowerShouldStartAsFollower() {
        when(syncMock.set(eq(LEADER_KEY), eq(CONSUMER_ID), any())).thenReturn("OK");
        when(settingsMock.COORDINATOR_SERVER_ROLE()).thenReturn(ServerRole.FOLLOWER);

        coordinator.spawnTasks();

        // Refresh follower claim
        verify(syncMock).set(eq(getFollowerClaimKey(CONSUMER_ID)), anyString(), any());
        verify(syncMock).expire(eq(getFollowerClaimKey(CONSUMER_ID)), any());
        verify(syncMock).expire(eq(getFollowerDevicesKey(CONSUMER_ID)), any());

        verify(leaderTaskMock).stop();
        verify(executorMock).submit(followerTaskMock);
    }

    private void configureSettingsMock() {
        when(settingsMock.SINGLE_INSTANCE_MODE()).thenReturn(false);
        when(settingsMock.COORDINATOR_CLAIM_INTERVAL()).thenReturn(1);
        when(settingsMock.COORDINATOR_SERVER_ROLE()).thenReturn(ServerRole.AUTO);
    }
}
