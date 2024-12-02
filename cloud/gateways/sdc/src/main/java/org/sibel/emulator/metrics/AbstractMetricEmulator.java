package org.sibel.emulator.metrics;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.constants.Metric;
import org.sibel.constants.SensorType;
import org.somda.sdc.biceps.common.MdibStateModifications;
import org.somda.sdc.biceps.model.participant.AbstractState;
import org.somda.sdc.biceps.provider.access.LocalMdibAccess;

public abstract class AbstractMetricEmulator implements Runnable {
    private static final Logger LOG = LogManager.getLogger(AbstractMetricEmulator.class);

    private boolean running = true;

    private final String name;
    private final LocalMdibAccess mdibAccess;
    protected final SensorType sensorType;
    protected final Metric metric;
    private final MdibStateModifications.Type metricType;
    protected final int bufferingRateMillis;

    public AbstractMetricEmulator(
            LocalMdibAccess mdibAccess,
            SensorType sensorType,
            Metric metric,
            MdibStateModifications.Type metricType,
            int bufferingRateMillis) {
        this.name = metric.name();
        this.sensorType = sensorType;
        this.metric = metric;
        this.bufferingRateMillis = bufferingRateMillis;
        this.mdibAccess = mdibAccess;
        this.metricType = metricType;
    }

    @Override
    public void run() {
        LOG.info("Emulation started for metric: {}", name);
        while (running) {
            try {
                Thread.sleep(bufferingRateMillis);
            } catch (InterruptedException e) {
                running = false;
            }
            writeNextMetric();
        }
        LOG.info("Emulation terminated for metric: {}", name);
    }

    public void stop() {
        running = false;
        Thread.currentThread().interrupt();
    }

    public void writeNextMetric() {
        try {
            var modifications = MdibStateModifications.create(metricType);
            modifications.add(getNextMetricState());
            mdibAccess.writeStates(modifications);
            LOG.debug("New metric state written for metric: {}", name);
        } catch (Exception e) {
            LOG.warn("Error writing new metric state", e);
        }
    }

    public abstract AbstractState getNextMetricState();
}
