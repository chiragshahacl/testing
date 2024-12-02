package org.sibel.models;

import com.google.common.base.Objects;
import java.time.Instant;
import java.util.List;
import java.util.Map;

public record CommandExecutionResponseBrokerMessage(
        String entityId,
        String eventName,
        Instant performedOn,
        String performedBy,
        EventState eventState,
        Map<String, Object> previousState,
        String entityName,
        String emittedBy,
        String eventType,
        String messageId)
        implements BrokerMessage {
    public record EventState(boolean success, List<String> errors) {
        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            EventState that = (EventState) o;
            return success == that.success;
        }

        @Override
        public int hashCode() {
            return Objects.hashCode(success);
        }
    }

    public static final String EVENT_NAME = "Command execution response";
    public static final String EVENT_TYPE = "COMMAND_EXECUTION_RESPONSE";
    public static final String ENTITY_NAME = "device";
    public static final String EMITTED_BY = "sdc";

    public static CommandExecutionResponseBrokerMessage createSuccessResponse(
            CommandEventBrokerMessage request, Instant timestamp) {
        return createSuccessResponse(request.entityId(), timestamp, request.performedBy(), request.messageId());
    }

    public static CommandExecutionResponseBrokerMessage createSuccessResponse(
            String entityId, Instant timestamp, String performedBy, String messageId) {
        return new CommandExecutionResponseBrokerMessage(
                entityId,
                EVENT_NAME,
                timestamp,
                performedBy,
                new EventState(true, List.of()),
                Map.of(),
                ENTITY_NAME,
                EMITTED_BY,
                EVENT_TYPE,
                messageId);
    }

    public static CommandExecutionResponseBrokerMessage createErrorResponse(
            List<String> errors, CommandEventBrokerMessage request, Instant timestamp) {
        return createErrorResponse(errors, request.entityId(), timestamp, request.performedBy(), request.messageId());
    }

    public static CommandExecutionResponseBrokerMessage createErrorResponse(
            List<String> errors, String entityId, Instant timestamp, String performedBy, String messageId) {
        return new CommandExecutionResponseBrokerMessage(
                entityId,
                EVENT_NAME,
                timestamp,
                performedBy,
                new EventState(false, errors),
                Map.of(),
                ENTITY_NAME,
                EMITTED_BY,
                EVENT_TYPE,
                messageId);
    }

    @Override
    public String getMessageId() {
        return messageId;
    }

    @Override
    public String getEventType() {
        return eventType;
    }
}
