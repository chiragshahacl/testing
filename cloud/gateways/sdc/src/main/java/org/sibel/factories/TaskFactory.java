package org.sibel.factories;

import org.sibel.tasks.DeviceConnectionCheckTask;

public interface TaskFactory {
    DeviceConnectionCheckTask createDeviceConnectionCheckTask(String serialNumber);
}
