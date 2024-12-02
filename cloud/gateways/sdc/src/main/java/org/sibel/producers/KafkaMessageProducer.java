package org.sibel.producers;

import java.util.List;
import org.apache.kafka.common.header.internals.RecordHeader;
import org.sibel.models.BrokerMessage;
import org.sibel.models.events.Event;

public interface KafkaMessageProducer {
    boolean isHealthy();

    void notify(BrokerMessage message, String topic, String key, List<RecordHeader> headers);

    void notify(Event event, String topic, String key, List<RecordHeader> headers);
}
