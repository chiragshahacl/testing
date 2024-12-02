package org.sibel.emulator;

import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.emulator.metrics.AbstractMetricEmulator;

public class DeviceEmulator {
    private static final Logger LOG = LogManager.getLogger();
    private final String name;
    private final List<AbstractMetricEmulator> metricEmulators;
    private final ExecutorService executor;

    public DeviceEmulator(String name, List<AbstractMetricEmulator> metricEmulators) {
        if (metricEmulators.isEmpty()) {
            throw new IllegalArgumentException("At least a metric emulator should be present");
        }

        this.name = name;
        this.metricEmulators = metricEmulators;
        executor = Executors.newFixedThreadPool(metricEmulators.size());
    }

    public void start() {
        metricEmulators.forEach(executor::submit);
        LOG.info("Emulation started for device: {}", name);
    }

    public void stop() {
        metricEmulators.forEach(AbstractMetricEmulator::stop);
        executor.close();
        LOG.info("Emulation stopped for device: {}", name);
    }
}
