package org.sibel.config;

import com.google.inject.Inject;
import java.util.List;
import org.sibel.constants.ServerRole;

public class SettingsImpl implements Settings {
    private final SettingStorage storage;

    @Inject
    public SettingsImpl(SettingStorage storage) {
        this.storage = storage;
    }

    @Override
    public int REMOTE_DEVICE_CONN_MAX_WAIT() {
        return storage.REMOTE_DEVICE_CONN_MAX_WAIT;
    }

    @Override
    public Integer CLAIM_INTERVAL() {
        return storage.CLAIM_INTERVAL;
    }

    @Override
    public int PATIENT_CLAIM_EXPIRATION() {
        return storage.PATIENT_CLAIM_EXPIRATION;
    }

    @Override
    public String ENVIRONMENT() {
        return storage.ENVIRONMENT;
    }

    @Override
    public String LOG_LEVEL() {
        return storage.LOG_LEVEL;
    }

    @Override
    public String HOST_IP_ADDR() {
        return storage.HOST_IP_ADDR;
    }

    @Override
    public String REDIS_HOST() {
        return storage.REDIS_HOST;
    }

    @Override
    public Integer REDIS_PORT() {
        return storage.REDIS_PORT;
    }

    @Override
    public String REDIS_USERNAME() {
        return storage.REDIS_USERNAME;
    }

    @Override
    public String REDIS_PASSWORD() {
        return storage.REDIS_PASSWORD;
    }

    @Override
    public String KAFKA_HOST() {
        return storage.KAFKA_HOST;
    }

    @Override
    public String KAFKA_PORT() {
        return storage.KAFKA_PORT;
    }

    @Override
    public String KAFKA_TOPIC_VITALS() {
        return storage.KAFKA_TOPIC_VITALS;
    }

    @Override
    public String KAFKA_CA_FILE() {
        return storage.KAFKA_CA_FILE;
    }

    @Override
    public String KAFKA_KEY_FILE_PATH() {
        return storage.KAFKA_KEY_FILE_PATH;
    }

    @Override
    public String KAFKA_PASSWORD() {
        return storage.KAFKA_PASSWORD;
    }

    @Override
    public Integer PROBE_INTERVAL() {
        return storage.PROBE_INTERVAL;
    }

    @Override
    public String KAFKA_TOPIC_DEVICE() {
        return storage.KAFKA_TOPIC_DEVICE;
    }

    @Override
    public String KAFKA_TOPIC_ALERT() {
        return storage.KAFKA_TOPIC_ALERT;
    }

    @Override
    public String KAFKA_TOPIC_SDC_REALTIME_STATE() {
        return storage.KAFKA_TOPIC_SDC_REALTIME_STATE;
    }

    @Override
    public String KAFKA_TOPIC_PATIENT_EVENTS() {
        return storage.KAFKA_TOPIC_PATIENT_EVENTS;
    }

    @Override
    public String KAFKA_TOPIC_HEALTH_CHECK() {
        return storage.KAFKA_TOPIC_HEALTH_CHECK;
    }

    @Override
    public String CRYPTO_USER_KEY_PATH() {
        return storage.CRYPTO_USER_KEY_PATH;
    }

    @Override
    public String CRYPTO_USER_CERT_PATH() {
        return storage.CRYPTO_USER_CERT_PATH;
    }

    @Override
    public String CRYPTO_CA_CERT_PATH() {
        return storage.CRYPTO_CA_CERT_PATH;
    }

    @Override
    public String CRYPTO_USER_KEY_PASSWORD() {
        return storage.CRYPTO_USER_KEY_PASSWORD;
    }

    @Override
    public Integer REALTIME_STATE_MESSAGE_DURATION() {
        return storage.REALTIME_STATE_MESSAGE_DURATION;
    }

    @Override
    public int HEALTH_CHECK_PORT() {
        return storage.HEALTH_CHECK_PORT;
    }

    @Override
    public boolean ALERTS_CACHE_ENABLED() {
        return storage.ALERTS_CACHE_ENABLED;
    }

    @Override
    public boolean VITALS_CACHE_ENABLED() {
        return storage.VITALS_CACHE_ENABLED;
    }

    @Override
    public boolean FEATURE_DETERMINATION_PERIOD_ENABLED() {
        return storage.FEATURE_DETERMINATION_PERIOD_ENABLED;
    }

    @Override
    public boolean SINGLE_INSTANCE_MODE() {
        return storage.SINGLE_INSTANCE_MODE;
    }

    @Override
    public int FOLLOWER_MAX_CONNECTED_DEVICES() {
        return storage.FOLLOWER_MAX_CONNECTED_DEVICES;
    }

    @Override
    public int COORDINATOR_CLAIM_INTERVAL() {
        return storage.COORDINATOR_CLAIM_INTERVAL;
    }

    @Override
    public ServerRole COORDINATOR_SERVER_ROLE() {
        return storage.COORDINATOR_SERVER_ROLE;
    }

    @Override
    public String JWT_PUBLIC_KEY() {
        return storage.JWT_PUBLIC_KEY;
    }

    @Override
    public String JWT_PRIVATE_KEY() {
        return storage.JWT_PRIVATE_KEY;
    }

    @Override
    public String PATIENT_SERVICE_URL() {
        return storage.PATIENT_SERVICE_URL;
    }

    @Override
    public String EHR_SERVICE_URL() {
        return storage.EHR_SERVICE_URL;
    }

    @Override
    public List<String> FINGERPRINT_BLACKLIST() {
        return storage.FINGERPRINT_BLACKLIST;
    }

    @Override
    public String CENTRAL_HUB_VALIDATOR_ID() {
        return storage.CENTRAL_HUB_VALIDATOR_ID;
    }

    @Override
    public String PATIENT_MONITOR_VALIDATOR_ID() {
        return storage.PATIENT_MONITOR_VALIDATOR_ID;
    }
}
