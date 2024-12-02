package org.sibel.utils;

import com.google.inject.Inject;
import com.google.inject.Singleton;
import io.lettuce.core.RedisClient;
import io.lettuce.core.RedisURI;
import io.lettuce.core.api.StatefulRedisConnection;
import io.lettuce.core.api.sync.RedisCommands;
import io.lettuce.core.pubsub.RedisPubSubListener;
import io.lettuce.core.pubsub.StatefulRedisPubSubConnection;
import java.util.HashMap;
import java.util.Map;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.config.Settings;
import org.sibel.exceptions.RedisUnavailable;

@Singleton
public class CacheClientImpl implements CacheClient {
    private static final Logger LOG = LogManager.getLogger();

    private final RedisClient client;
    private final Map<String, StatefulRedisPubSubConnection<String, String>> pubSubConnections = new HashMap<>();

    private StatefulRedisConnection<String, String> syncConnection;

    @Inject
    public CacheClientImpl(Settings settings) throws RedisUnavailable {
        var redisBuilder = RedisURI.Builder.redis(settings.REDIS_HOST(), settings.REDIS_PORT());
        if (!settings.ENVIRONMENT().equals("local")) {
            redisBuilder.withAuthentication(
                    settings.REDIS_USERNAME(), settings.REDIS_PASSWORD().toCharArray());
        }
        client = RedisClient.create(redisBuilder.build());

        initConnection();
    }

    private synchronized void initConnection() {
        try {
            if (syncConnection == null || !syncConnection.isOpen()) {
                syncConnection = client.connect();
            }
        } catch (Exception e) {
            throw new RedisUnavailable("Failed to connect to Redis", e);
        }
    }

    @Override
    public synchronized boolean isHealthy() {
        var healthy = false;

        try {
            var pong = syncConnection.sync().ping();
            if (pong.equals("PONG")) {
                healthy = true;
            } else {
                LOG.error("Redis service not responding");
            }
        } catch (Exception e) {
            LOG.error("Redis service not responding", e);
        }

        return healthy;
    }

    @Override
    public synchronized RedisCommands<String, String> getRedisCommands() {
        initConnection();
        return syncConnection.sync();
    }

    @Override
    public synchronized void registerPubSubListener(String channel, RedisPubSubListener<String, String> listener) {
        try {
            var pubSubConnection = client.connectPubSub();
            pubSubConnections.put(channel, pubSubConnection);
            pubSubConnection.addListener(listener);
            pubSubConnection.sync().subscribe(channel);
        } catch (Exception e) {
            throw new RedisUnavailable("Failed to register pub sub listener", e);
        }
    }

    @Override
    public synchronized void unregisterPubSubListener(String channel, RedisPubSubListener<String, String> listener) {
        try {
            var pubSubConnection = pubSubConnections.get(channel);
            pubSubConnection.sync().unsubscribe(channel);
            pubSubConnection.removeListener(listener);
            pubSubConnection.close();
        } catch (Exception e) {
            throw new RedisUnavailable("Failed to unregister pub sub listener", e);
        }
    }
}
