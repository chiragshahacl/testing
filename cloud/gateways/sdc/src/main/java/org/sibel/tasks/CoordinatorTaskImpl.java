package org.sibel.tasks;

import static org.sibel.constants.RedisKeys.*;

import com.google.inject.Inject;
import com.google.inject.name.Named;
import io.lettuce.core.SetArgs;
import io.lettuce.core.api.sync.RedisCommands;
import java.time.Duration;
import java.util.Objects;
import java.util.concurrent.ExecutorService;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.config.Settings;
import org.sibel.constants.DI;
import org.sibel.constants.ServerRole;

public class CoordinatorTaskImpl implements CoordinatorTask {
    private static final Logger LOG = LogManager.getLogger();

    private final String consumerId;
    private final LeaderTask leaderTask;
    private final FollowerTask followerTask;
    private final KafkaConsumerTask kafkaConsumerTask;
    private final RedisCommands<String, String> sync;
    private final ExecutorService executor;
    private final Settings settings;
    private final Duration claimExpiration;

    private boolean isLeader;
    private boolean isRunning = true;

    @Inject
    public CoordinatorTaskImpl(
            @Named(DI.CONSUMER_ID) String consumerId,
            LeaderTask leaderTask,
            FollowerTask followerTask,
            KafkaConsumerTask kafkaConsumerTask,
            RedisCommands<String, String> sync,
            ExecutorService executor,
            Settings settings) {
        this.consumerId = consumerId;
        this.leaderTask = leaderTask;
        this.followerTask = followerTask;
        this.kafkaConsumerTask = kafkaConsumerTask;
        this.sync = sync;
        this.executor = executor;
        this.settings = settings;

        claimExpiration = Duration.ofSeconds(settings.COORDINATOR_CLAIM_INTERVAL() + 1);
    }

    @Override
    public Integer call() {
        if (settings.SINGLE_INSTANCE_MODE()) {
            LOG.info("Running in single instance mode");
        }
        while (isRunning) {
            try {
                spawnTasks();
                Thread.sleep(settings.COORDINATOR_CLAIM_INTERVAL() * 1000L);
            } catch (InterruptedException e) {
                isRunning = false;
                throw new RuntimeException(e);
            }
        }
        LOG.error("Coordinator task stopped");
        return -1;
    }

    @Override
    public boolean isHealthy() {
        return isRunning
                && (settings.SINGLE_INSTANCE_MODE() && leaderTask.isRunning() && followerTask.isRunning()
                        || isLeader && leaderTask.isRunning()
                        || followerTask.isRunning());
    }

    public void spawnTasks() {
        tryClaimLeadership();
        refreshClaims();

        if (settings.SINGLE_INSTANCE_MODE()) {
            // Must run both tasks
            if (!leaderTask.isRunning()) {
                executor.submit(leaderTask);
            }
            if (!followerTask.isRunning()) {
                executor.submit(followerTask);
            }
            if (!kafkaConsumerTask.isRunning()) {
                executor.submit(kafkaConsumerTask);
            }
        } else {
            if (isLeader && !leaderTask.isRunning()) {
                LOG.info("Leadership claimed, starting server as leader.");
                followerTask.stop();
                kafkaConsumerTask.stop();
                executor.submit(leaderTask);
            } else if (!isLeader && !followerTask.isRunning()) {
                LOG.info("Starting server as follower.");
                leaderTask.stop();
                executor.submit(followerTask);
                if (!kafkaConsumerTask.isRunning()) {
                    executor.submit(kafkaConsumerTask);
                }
            }
        }
    }

    private void tryClaimLeadership() {
        var serverRole = settings.COORDINATOR_SERVER_ROLE();

        if (serverRole == ServerRole.AUTO) {
            isLeader = false;
            var leadershipClaimed = sync.set(
                    LEADER_KEY, consumerId, SetArgs.Builder.ex(claimExpiration).nx());
            if (leadershipClaimed != null && leadershipClaimed.equals("OK")) {
                isLeader = true;
            } else {
                var leaderId = sync.get(LEADER_KEY);
                if (Objects.equals(leaderId, consumerId)) {
                    isLeader = true;
                }
            }
        } else {
            isLeader = serverRole == ServerRole.LEADER;
        }
    }

    private void refreshClaims() {
        if (isLeader || settings.SINGLE_INSTANCE_MODE()) {
            refreshLeaderClaim();
        }
        if (!isLeader || settings.SINGLE_INSTANCE_MODE()) {
            refreshFollowerClaim();
        }
    }

    private void refreshLeaderClaim() {
        sync.set(LEADER_KEY, consumerId, SetArgs.Builder.ex(claimExpiration).xx());
        LOG.info("Leader claim refreshed with id {}.", consumerId);
    }

    private void refreshFollowerClaim() {
        sync.set(
                getFollowerClaimKey(consumerId),
                "OK",
                SetArgs.Builder.ex(claimExpiration).nx());
        sync.expire(getFollowerClaimKey(consumerId), claimExpiration);
        sync.expire(getFollowerDevicesKey(consumerId), claimExpiration);
        LOG.info("Follower claim refreshed with id {}.", consumerId);
    }
}
