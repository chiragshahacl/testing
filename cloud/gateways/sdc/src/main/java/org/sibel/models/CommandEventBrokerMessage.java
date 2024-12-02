package org.sibel.models;

import java.time.Instant;

public record CommandEventBrokerMessage(
        String entityId,
        String eventName,
        String commandName,
        String pmIdentifier,
        String requestId,
        Instant performedOn,
        String performedBy,
        String entityName,
        String emittedBy,
        String eventType,
        String messageId,
        String rawJsonParams) {}
