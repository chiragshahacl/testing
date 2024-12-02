package org.sibel.utils;

import io.lettuce.core.api.sync.RedisCommands;
import io.lettuce.core.pubsub.RedisPubSubListener;

public interface CacheClient {
    boolean isHealthy();

    RedisCommands<String, String> getRedisCommands();

    void registerPubSubListener(String channel, RedisPubSubListener<String, String> listener);

    void unregisterPubSubListener(String channel, RedisPubSubListener<String, String> listener);
}
