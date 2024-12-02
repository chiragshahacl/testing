package org.sibel.models;

import com.google.common.base.MoreObjects;
import com.google.common.base.Objects;
import java.time.Instant;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.models.payloads.PayloadInterface;

@SuppressWarnings("PMD.UnusedPrivateField")
public abstract class AbstractBrokerMessage implements BrokerMessage {
    protected static final Logger LOG = LogManager.getLogger(AbstractBrokerMessage.class);
    private String message_id;
    private String event_name;
    private String event_type;
    private Instant timestamp;
    private PayloadInterface payload;

    public AbstractBrokerMessage(
            String message_id, String event_name, String event_type, Instant timestamp, PayloadInterface payload) {
        this.message_id = message_id;
        this.event_name = event_name;
        this.event_type = event_type;
        this.timestamp = timestamp;
        this.payload = payload;
    }

    @Override
    public String getMessageId() {
        return message_id;
    }

    @Override
    public String getEventType() {
        return event_type;
    }

    public PayloadInterface getPayload() {
        return payload;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        AbstractBrokerMessage that = (AbstractBrokerMessage) o;
        return Objects.equal(message_id, that.message_id)
                && Objects.equal(event_name, that.event_name)
                && Objects.equal(event_type, that.event_type)
                && Objects.equal(timestamp, that.timestamp)
                && Objects.equal(payload, that.payload);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(message_id, event_name, event_type, timestamp, payload);
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("message_id", message_id)
                .add("event_name", event_name)
                .add("event_type", event_type)
                .add("timestamp", timestamp)
                .add("payload", payload)
                .toString();
    }
}
