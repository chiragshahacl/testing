package org.sibel.models.payloads.internal;

import com.google.common.base.MoreObjects;
import com.google.common.base.Objects;
import java.util.List;
import org.sibel.models.payloads.AlertPayload;

@SuppressWarnings("PMD.UnusedPrivateField")
public class DevicePayload {

    private String primary_identifier;
    private String name;
    private String gateway_id;
    private String device_code;
    private List<SensorPayload> connected_sensors;
    private List<AlertPayload> alerts;
    private ConfigPayload config;

    public DevicePayload(SensorPayload sensor, List<AlertPayload> alerts, String gatewayId, ConfigPayload config) {
        this(sensor.primary_identifier(), sensor.name(), gatewayId, sensor.device_code(), null, alerts, config);
    }

    public DevicePayload(
            String primaryIdentifier,
            String name,
            String gatewayId,
            String deviceCode,
            List<SensorPayload> connectedSensors,
            List<AlertPayload> alerts,
            ConfigPayload config) {
        this.primary_identifier = primaryIdentifier;
        this.name = name;
        this.gateway_id = gatewayId;
        this.device_code = deviceCode;
        connected_sensors = connectedSensors;
        this.alerts = alerts;
        this.config = config;
    }

    public String getPrimaryIdentifier() {
        return primary_identifier;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        DevicePayload that = (DevicePayload) o;
        return Objects.equal(primary_identifier, that.primary_identifier)
                && Objects.equal(name, that.name)
                && Objects.equal(gateway_id, that.gateway_id)
                && Objects.equal(device_code, that.device_code)
                && Objects.equal(connected_sensors, that.connected_sensors)
                && Objects.equal(alerts, that.alerts)
                && Objects.equal(config, that.config);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(primary_identifier, name, gateway_id, device_code, connected_sensors, alerts, config);
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("primary_identifier", primary_identifier)
                .add("name", name)
                .add("gateway_id", gateway_id)
                .add("device_code", device_code)
                .add("connected_sensors", connected_sensors)
                .add("alerts", alerts)
                .add("config", config)
                .toString();
    }
}
