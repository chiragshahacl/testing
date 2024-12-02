package org.sibel.models.payloads;

public record PmConfigurationUpdatedPayload(
        String devicePrimaryIdentifier, boolean audioEnabled, boolean audioPauseEnabled) implements PayloadInterface {}
