package org.sibel.tasks;

import com.google.gson.Gson;
import com.google.gson.JsonParseException;
import com.google.inject.Inject;
import com.google.inject.Injector;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.Callable;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.PatientMonitor;
import org.sibel.config.Settings;
import org.sibel.constants.EventTypes;
import org.sibel.consumers.KafkaMessageConsumer;
import org.sibel.exceptions.CommandExecutionFailure;
import org.sibel.exceptions.KafkaUnavailable;
import org.sibel.exceptions.ScoOperationException;
import org.sibel.models.IncomingBrokerMessage;
import org.sibel.models.PatientEncounterPlannedMessage;
import org.sibel.models.scoParams.SetPatientContextParams;
import org.sibel.repositories.PatientMonitorRepository;
import org.sibel.sco.AbstractScoOperation;
import org.sibel.sco.SetPatientContextScoOperation;

public class KafkaConsumerTask implements Callable<Integer> {
    private static final Logger LOG = LogManager.getLogger();

    private final KafkaMessageConsumer kafkaConsumer;
    private final Settings settings;
    private final Gson gson;
    private final PatientMonitorRepository patientMonitorRepository;
    private final Map<String, AbstractScoOperation> registeredScoOperations = new HashMap<>();

    private boolean running;

    @Inject
    public KafkaConsumerTask(
            KafkaMessageConsumer kafkaConsumer,
            Settings settings,
            Gson gson,
            PatientMonitorRepository patientMonitorRepository,
            Injector injector) {
        this.kafkaConsumer = kafkaConsumer;
        this.settings = settings;
        this.gson = gson;
        this.patientMonitorRepository = patientMonitorRepository;

        // Register all operations
        var setPatientContextScoOperation = injector.getInstance(SetPatientContextScoOperation.class);
        registerOperation(setPatientContextScoOperation);
    }

    @Override
    public Integer call() {
        running = true;
        try {
            kafkaConsumer.subscribeToTopic(settings.KAFKA_TOPIC_PATIENT_EVENTS());

            LOG.info("Kafka Consumer task started.");
            while (running) {
                var records = kafkaConsumer.poll(Duration.ofMillis(100));

                for (var record : records) {
                    var rawBrokerMessage = record.value();
                    handleBrokerMessageReceived(rawBrokerMessage);
                }
            }
        } catch (KafkaUnavailable e) {
            LOG.error("Failed to send notification to Central Hub", e);
        }
        return 0;
    }

    public void handleBrokerMessageReceived(String rawMessage) {
        try {
            var message = gson.fromJson(rawMessage, IncomingBrokerMessage.class);
            if (Objects.equals(message.eventType(), EventTypes.PATIENT_ENCOUNTER_PLANNED)) {
                LOG.info("Handling patient encounter planned.");
                handlePatientEncounterPlanned(rawMessage);
            } else {
                LOG.debug("Ignoring message of type {}.", message.eventType());
            }
        } catch (JsonParseException e) {
            LOG.error("Error parsing message received: {}", rawMessage, e);
        }
    }

    public void stop() {
        if (running) {
            running = false;
            LOG.info("Kafka Consumer task stopped.");
        }
    }

    public boolean isRunning() {
        return running;
    }

    private void registerOperation(AbstractScoOperation operation) {
        registeredScoOperations.putIfAbsent(operation.getName(), operation);
    }

    private void handlePatientEncounterPlanned(String rawMessage) {
        try {
            var operation = getScoOperation(SetPatientContextScoOperation.OPERATION_NAME);
            var message = gson.fromJson(rawMessage, PatientEncounterPlannedMessage.class);
            var patientMonitor = getPatientMonitor(message.pmId());
            var params = SetPatientContextParams.fromPatientEncounterPlannedMessage(message);
            executeCommand(operation, patientMonitor, params);
        } catch (CommandExecutionFailure e) {
            LOG.error("Error executing set patient context SCO.", e);
            // TODO: Maybe we could send an error message back to the CMS here
        }
    }

    private AbstractScoOperation getScoOperation(String operationName) throws CommandExecutionFailure {
        var scoOperationData = registeredScoOperations.get(operationName);
        if (scoOperationData == null) {
            throw new CommandExecutionFailure(
                    "No SCO operation registered with the name \"%s\"".formatted(operationName));
        }
        return scoOperationData;
    }

    private PatientMonitor getPatientMonitor(String serialNumber) throws CommandExecutionFailure {
        var patientMonitor = patientMonitorRepository.getBySerialNumber(serialNumber);
        if (patientMonitor == null) {
            throw new CommandExecutionFailure("No PM registered with the identifier \"%s\"");
        }
        return patientMonitor;
    }

    private void executeCommand(AbstractScoOperation operation, PatientMonitor patientMonitor, Object params)
            throws CommandExecutionFailure {
        try {
            if (operation.isEnabledFor(patientMonitor)) {
                operation.run(patientMonitor, params);
            } else {
                throw new CommandExecutionFailure(
                        "The %s operation is not enabled for %s".formatted(operation, patientMonitor));
            }
        } catch (ScoOperationException e) {
            throw new CommandExecutionFailure("Failed to execute %s for %s".formatted(operation, patientMonitor), e);
        }
    }
}
