package org.sibel.consumers;

import java.time.Duration;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.sibel.exceptions.KafkaUnavailable;

public interface KafkaMessageConsumer {
    boolean isHealthy();

    void subscribeToTopic(String topic) throws KafkaUnavailable;

    ConsumerRecords<String, String> poll(Duration duration) throws KafkaUnavailable;
}
