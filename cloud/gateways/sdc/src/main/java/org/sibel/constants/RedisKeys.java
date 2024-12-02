package org.sibel.constants;

public final class RedisKeys {
    public static final String LEADER_KEY = "sdc/leader";

    private static final String DEVICE_CLAIM_PREFIX = "sdc/device/claim";
    private static final String DEVICE_PRIMARY_IDENTIFIER_PREFIX = "sdc/device/primaryIdentifier";
    private static final String FOLLOWER_CLAIM_PREFIX = "sdc/follower/claim";
    private static final String FOLLOWER_DEVICES_PREFIX = "sdc/follower/devices";
    private static final String FOLLOWER_CHANNEL_PREFIX = "sdc/follower/devices";
    private static final String SHARED_PATIENT_ID_PREFIX = "shared/monitoring/patient";

    public static String getDeviceKey(String deviceEpr) {
        return String.format("%s/%s", DEVICE_CLAIM_PREFIX, deviceEpr);
    }

    public static String getDevicePrimaryIdentifierKey(String deviceEpr) {
        return String.format("%s/%s", DEVICE_PRIMARY_IDENTIFIER_PREFIX, deviceEpr);
    }

    public static String getFollowerClaimKey(String followerId) {
        return String.format("%s/%s", FOLLOWER_CLAIM_PREFIX, followerId);
    }

    public static String getFollowerIdFromClaimKey(String followerKey) {
        return followerKey.substring(FOLLOWER_CLAIM_PREFIX.length() + 1);
    }

    public static String getFollowerDevicesKey(String consumerId) {
        return String.format("%s/%s", FOLLOWER_DEVICES_PREFIX, consumerId);
    }

    public static String getFollowerChannelKey(String consumerId) {
        return String.format("%s/%s", FOLLOWER_CHANNEL_PREFIX, consumerId);
    }

    public static String getSharedPatientIdKey(String primaryIdentifier) {
        return "%s/%s".formatted(SHARED_PATIENT_ID_PREFIX, primaryIdentifier);
    }
}
