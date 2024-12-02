package org.sibel.config;

import java.util.List;
import org.sibel.constants.ServerRole;

public interface Settings {
    int REMOTE_DEVICE_CONN_MAX_WAIT();

    Integer CLAIM_INTERVAL();

    int PATIENT_CLAIM_EXPIRATION();

    String ENVIRONMENT();

    String LOG_LEVEL();

    String HOST_IP_ADDR();

    String REDIS_HOST();

    Integer REDIS_PORT();

    String REDIS_USERNAME();

    String REDIS_PASSWORD();

    String KAFKA_HOST();

    String KAFKA_PORT();

    String KAFKA_CA_FILE();

    String KAFKA_KEY_FILE_PATH();

    String KAFKA_PASSWORD();

    Integer PROBE_INTERVAL();

    String KAFKA_TOPIC_VITALS();

    String KAFKA_TOPIC_DEVICE();

    String KAFKA_TOPIC_ALERT();

    String KAFKA_TOPIC_SDC_REALTIME_STATE();

    String KAFKA_TOPIC_PATIENT_EVENTS();

    String KAFKA_TOPIC_HEALTH_CHECK();

    String CRYPTO_USER_KEY_PATH();

    String CRYPTO_USER_CERT_PATH();

    String CRYPTO_CA_CERT_PATH();

    String CRYPTO_USER_KEY_PASSWORD();

    Integer REALTIME_STATE_MESSAGE_DURATION();

    int HEALTH_CHECK_PORT();

    boolean ALERTS_CACHE_ENABLED();

    boolean VITALS_CACHE_ENABLED();

    boolean FEATURE_DETERMINATION_PERIOD_ENABLED();

    boolean SINGLE_INSTANCE_MODE();

    int FOLLOWER_MAX_CONNECTED_DEVICES();

    int COORDINATOR_CLAIM_INTERVAL();

    ServerRole COORDINATOR_SERVER_ROLE();

    String JWT_PUBLIC_KEY();

    String JWT_PRIVATE_KEY();

    String PATIENT_SERVICE_URL();

    String EHR_SERVICE_URL();

    List<String> FINGERPRINT_BLACKLIST();

    String CENTRAL_HUB_VALIDATOR_ID();

    String PATIENT_MONITOR_VALIDATOR_ID();
}
