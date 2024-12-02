package org.sibel.constants;

public final class MdibHandles {
    public static final String ROOT_HANDLE = "sibel.anneone";
    public static final String SYSTEM_CONTEXT_HANDLE = "sibel.anneone.sc";
    public static final String PATIENT_CONTEXT_HANDLE = "sibel.anneone.pc";
    public static final String PATIENT_CONTEXT_STATE_HANDLE = "sibel.anneone.pc.state";

    public static String getBatteryHandle(SensorType sensorType) {
        return String.format("%s.battery.%s", ROOT_HANDLE, sensorType.handle);
    }

    public static String getDeviceHandle(SensorType sensorType) {
        return String.format("%s.%s", ROOT_HANDLE, sensorType.handle);
    }

    public static String getMetricChannelHandle(SensorType sensorType, MetricChannel channel) {
        return String.format("%s.%s", getDeviceHandle(sensorType), channel.name);
    }

    public static String getMetricHandle(SensorType sensorType, Metric metric) {
        return String.format("%s.%s", getMetricChannelHandle(sensorType, metric.channel), metric.handle);
    }

    public static String getAlertSystemHandle(SensorType sensorType) {
        return String.format("%s.alertsystem", sensorType == SensorType.PM ? ROOT_HANDLE : getDeviceHandle(sensorType));
    }

    public static String getAlertConditionHandle(SensorType sensorType, TechnicalAlert alert) {
        return String.format("%s.condition.%s", getAlertSystemHandle(sensorType), alert.handle);
    }

    public static String getAlertConditionHandle(PhysiologicalAlert alert) {
        return String.format("%s.condition.%s", getAlertSystemHandle(SensorType.PM), alert.condition.handle);
    }

    public static String getAlertSignalHandle(SensorType sensorType, TechnicalAlert alert) {
        return String.format("%s.signal.vis.%s", getAlertSystemHandle(sensorType), alert.handle);
    }

    public static String getAlertSignalHandle(PhysiologicalAlert alert) {
        return String.format(
                "%s.signal.%s.%s", getAlertSystemHandle(SensorType.PM), alert.manifestation, alert.condition.handle);
    }

    public static String getScoHandle(SensorType sensorType) {
        return "sibel.anneone.sco.%s".formatted(sensorType.handle);
    }

    public static String getOperationHandle(SensorType sensorType, ScoOperationType operationType) {
        return "%s.%s".formatted(getScoHandle(sensorType), operationType.handle);
    }
}
