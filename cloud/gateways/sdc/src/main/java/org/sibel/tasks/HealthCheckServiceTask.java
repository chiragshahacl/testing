package org.sibel.tasks;

import com.google.inject.Inject;
import java.io.IOException;
import java.net.ServerSocket;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.ExtendedExecutor;
import org.sibel.config.Settings;
import org.sibel.consumers.KafkaMessageConsumer;
import org.sibel.producers.KafkaMessageProducer;
import org.sibel.utils.CacheClient;

public class HealthCheckServiceTask implements Callable<Integer> {
    private static final Logger LOG = LogManager.getLogger();

    private ServerSocket serverSocket = null;
    private boolean isStopped = false;

    private final int serverPort;
    private final ExtendedExecutor executor;
    private final CoordinatorTask coordinatorTask;
    private final CacheClient cacheClient;
    private final KafkaMessageProducer producer;
    private final KafkaMessageConsumer consumer;

    @Inject
    public HealthCheckServiceTask(
            Settings settings,
            ExecutorService executor,
            CoordinatorTask coordinatorTask,
            CacheClient cacheClient,
            KafkaMessageProducer producer,
            KafkaMessageConsumer consumer) {
        this.serverPort = settings.HEALTH_CHECK_PORT();
        this.executor = (ExtendedExecutor) executor;
        this.coordinatorTask = coordinatorTask;
        this.cacheClient = cacheClient;
        this.producer = producer;
        this.consumer = consumer;
    }

    @Override
    public Integer call() {
        try {
            serverSocket = new ServerSocket(serverPort);
            while (!isStopped()) {
                var clientSocket = serverSocket.accept();
                var isHealthy = coordinatorTask.isHealthy()
                        && cacheClient.isHealthy()
                        && producer.isHealthy()
                        && consumer.isHealthy()
                        && !executor.hasError();
                var errorMessage = "";
                if (!coordinatorTask.isHealthy()) {
                    errorMessage += "Coordinator: Not running\n";
                }
                if (!cacheClient.isHealthy()) {
                    errorMessage += "Redis: Failed to connect\n";
                }
                if (!producer.isHealthy() || !consumer.isHealthy()) {
                    errorMessage += "Kafka: Failed to connect\n";
                }
                if (executor.hasError()) {
                    errorMessage += "Executor: %s\n".formatted(executor.getErrorMessage());
                }
                executor.submit(new HealthCheckRequestTask(clientSocket, isHealthy, errorMessage.trim()));
            }
        } catch (IOException e1) {
            throw new RuntimeException("Error running health check on port %s".formatted(serverPort), e1);
        }
        LOG.info("Health check server stopped.");
        return 0;
    }

    private synchronized boolean isStopped() {
        return isStopped;
    }

    public synchronized void stop() {
        isStopped = true;
        try {
            if (serverSocket != null) {
                serverSocket.close();
            }
        } catch (IOException e) {
            throw new RuntimeException("Error closing server", e);
        }
    }
}
