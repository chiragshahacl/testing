package org.sibel.config;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Base64;
import java.util.List;
import org.sibel.constants.ServerRole;

public class SettingStorage {
    @SettingValue(variableName = "ENVIRONMENT", configurationName = "env.name")
    public String ENVIRONMENT;

    @SettingValue(variableName = "LOG_LEVEL", configurationName = "log.level", defaultValue = "INFO")
    public String LOG_LEVEL;

    @SettingValue(variableName = "HOST_IP_ADDR", configurationName = "host.ip")
    public String HOST_IP_ADDR;

    @SettingValue(variableName = "HEALTH_CHECK_PORT", configurationName = "healthCheck.port", defaultValue = "80")
    public int HEALTH_CHECK_PORT;

    @SettingValue(
            variableName = "REMOTE_DEVICE_CONN_MAX_WAIT",
            configurationName = "remoteDevice.connection.maxWait",
            defaultValue = "10")
    public int REMOTE_DEVICE_CONN_MAX_WAIT;

    @SettingValue(
            variableName = "ALERTS_CACHE_ENABLED",
            configurationName = "alertsCache.enabled",
            defaultValue = "false")
    public boolean ALERTS_CACHE_ENABLED;

    @SettingValue(
            variableName = "VITALS_CACHE_ENABLED",
            configurationName = "vitalsCache.enabled",
            defaultValue = "false")
    public boolean VITALS_CACHE_ENABLED;

    @SettingValue(
            variableName = "SINGLE_INSTANCE_MODE",
            configurationName = "host.singleInstanceMode",
            defaultValue = "false")
    public boolean SINGLE_INSTANCE_MODE;

    @SettingValue(variableName = "FOLLOWER_MAX_CONNECTED_DEVICES", configurationName = "follower.maxConnectedDevices")
    public int FOLLOWER_MAX_CONNECTED_DEVICES;

    @SettingValue(
            variableName = "COORDINATOR_CLAIM_INTERVAL",
            configurationName = "coordinator.claimInterval",
            defaultValue = "15")
    public int COORDINATOR_CLAIM_INTERVAL;

    @SettingValue(
            variableName = "COORDINATOR_SERVER_ROLE",
            configurationName = "coordinator.serverRole",
            defaultValue = "AUTO",
            parserMethod = "parseServerRole")
    public ServerRole COORDINATOR_SERVER_ROLE;

    @SettingValue(variableName = "REDIS_HOST", configurationName = "redis.host")
    public String REDIS_HOST;

    @SettingValue(variableName = "REDIS_PORT", configurationName = "redis.port")
    public int REDIS_PORT;

    @SettingValue(variableName = "REDIS_USERNAME", configurationName = "redis.username", required = false)
    public String REDIS_USERNAME;

    @SettingValue(variableName = "REDIS_PASSWORD", configurationName = "redis.password", required = false)
    public String REDIS_PASSWORD;

    @SettingValue(variableName = "KAFKA_HOST", configurationName = "kafka.host")
    public String KAFKA_HOST;

    @SettingValue(variableName = "KAFKA_PORT", configurationName = "kafka.port")
    public String KAFKA_PORT;

    @SettingValue(variableName = "KAFKA_TOPIC_VITALS", configurationName = "kafka.vitalTopic")
    public String KAFKA_TOPIC_VITALS;

    @SettingValue(
            variableName = "KAFKA_CA_FILE_PATH",
            configurationName = "kafka.caFilePath",
            required = false,
            parserMethod = "getFile")
    public String KAFKA_CA_FILE;

    @SettingValue(variableName = "KAFKA_KEY_FILE_PATH", configurationName = "kafka.keyFilePath", required = false)
    public String KAFKA_KEY_FILE_PATH;

    @SettingValue(variableName = "KAFKA_PASSWORD", configurationName = "kafka.password", required = false)
    public String KAFKA_PASSWORD;

    @SettingValue(variableName = "KAFKA_TOPIC_DEVICE", configurationName = "kafka.deviceTopic")
    public String KAFKA_TOPIC_DEVICE;

    @SettingValue(variableName = "KAFKA_TOPIC_ALERT", configurationName = "kafka.alertTopic")
    public String KAFKA_TOPIC_ALERT;

    @SettingValue(variableName = "KAFKA_TOPIC_SDC_REALTIME_STATE", configurationName = "kafka.realtimeStateTopic")
    public String KAFKA_TOPIC_SDC_REALTIME_STATE;

    @SettingValue(variableName = "KAFKA_TOPIC_PATIENT_EVENTS", configurationName = "kafka.patientEvents")
    public String KAFKA_TOPIC_PATIENT_EVENTS;

    @SettingValue(variableName = "KAFKA_TOPIC_HEALTH_CHECK", configurationName = "kafka.healthCheck")
    public String KAFKA_TOPIC_HEALTH_CHECK;

    @SettingValue(
            variableName = "REALTIME_STATE_MESSAGE_DURATION",
            configurationName = "kafka.realtimeStateMessageDuration")
    public int REALTIME_STATE_MESSAGE_DURATION;

    @SettingValue(variableName = "PROBE_INTERVAL", configurationName = "host.discoveryIntervalSeconds")
    public int PROBE_INTERVAL;

    @SettingValue(variableName = "CLAIM_INTERVAL", configurationName = "redis.refreshClaimInterval")
    public int CLAIM_INTERVAL;

    @SettingValue(
            variableName = "PATIENT_CLAIM_EXPIRATION",
            configurationName = "redis.patientClaimExpiration",
            defaultValue = "10")
    public int PATIENT_CLAIM_EXPIRATION;

    @SettingValue(variableName = "CRYPTO_USER_KEY_PATH", configurationName = "crypto.userKeyPath")
    public String CRYPTO_USER_KEY_PATH;

    @SettingValue(variableName = "CRYPTO_USER_CERT_PATH", configurationName = "crypto.userCertPath")
    public String CRYPTO_USER_CERT_PATH;

    @SettingValue(variableName = "CRYPTO_CA_CERT_PATH", configurationName = "crypto.caCertPath")
    public String CRYPTO_CA_CERT_PATH;

    @SettingValue(variableName = "CRYPTO_USER_KEY_PASSWORD", configurationName = "crypto.userKeyPassword")
    public String CRYPTO_USER_KEY_PASSWORD;

    @SettingValue(
            variableName = "FEATURE_DETERMINATION_PERIOD_ENABLED",
            configurationName = "feature.determinationPeriod.enabled",
            defaultValue = "false")
    public boolean FEATURE_DETERMINATION_PERIOD_ENABLED;

    @SettingValue(variableName = "PATIENT_SERVICE_URL", configurationName = "patientService.url")
    public String PATIENT_SERVICE_URL;

    @SettingValue(variableName = "EHR_SERVICE_URL", configurationName = "ehrService.url")
    public String EHR_SERVICE_URL;

    @SettingValue(variableName = "JWT_PUBLIC_KEY", configurationName = "jwt.publicKey", parserMethod = "parseBase64")
    public String JWT_PUBLIC_KEY;

    @SettingValue(variableName = "JWT_PRIVATE_KEY", configurationName = "jwt.privateKey", parserMethod = "parseBase64")
    public String JWT_PRIVATE_KEY;

    @SettingValue(
            variableName = "FINGERPRINT_BLACKLIST",
            configurationName = "crypto.fingerprintBlacklist",
            required = false,
            parserMethod = "parseFingerprintBlacklist")
    public List<String> FINGERPRINT_BLACKLIST;

    @SettingValue(variableName = "CENTRAL_HUB_VALIDATOR_ID", configurationName = "patientFlow.centralHubValidatorId")
    public String CENTRAL_HUB_VALIDATOR_ID;

    @SettingValue(
            variableName = "PATIENT_MONITOR_VALIDATOR_ID",
            configurationName = "patientFlow.patientMonitorValidatorId")
    public String PATIENT_MONITOR_VALIDATOR_ID;

    public static ServerRole parseServerRole(String role) {
        try {
            return ServerRole.valueOf(role.toUpperCase());
        } catch (IllegalArgumentException e) {
            return ServerRole.AUTO;
        }
    }

    public static String parseBase64(String encodedString) {
        var decodedBytes = Base64.getDecoder().decode(encodedString);
        return new String(decodedBytes);
    }

    public static List<String> parseFingerprintBlacklist(String rawBlacklist) {
        var rawBlacklistStream = Arrays.stream(rawBlacklist.split("\n"));
        // The fingerprint is in hexadecimal which can be either a continuous string
        // or be separated by colons like so: CD:F3:0D:0D:7F:8C:88:5B:38:7E:04:E8:A8:27:BE:F1:C3:8C:30:B7
        return rawBlacklistStream
                .map(fingerprint -> fingerprint.replace(":", ""))
                .map(String::strip)
                .toList();
    }

    public static String getFile(String path) {
        List<String> lines;
        try {
            lines = Files.readAllLines(Path.of(path));
        } catch (IOException e) {
            throw new RuntimeException(String.format("Unable to open settings file %s", path), e);
        }
        return String.join("\n", lines);
    }
}
