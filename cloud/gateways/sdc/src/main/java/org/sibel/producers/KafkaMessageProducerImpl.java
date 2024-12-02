package org.sibel.producers;

import com.google.gson.Gson;
import com.google.inject.Inject;
import java.util.*;
import org.apache.kafka.clients.CommonClientConfigs;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.KafkaException;
import org.apache.kafka.common.config.SslConfigs;
import org.apache.kafka.common.header.internals.RecordHeader;
import org.apache.kafka.common.serialization.StringSerializer;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.config.Settings;
import org.sibel.constants.KafkaHeaders;
import org.sibel.exceptions.KafkaUnavailable;
import org.sibel.models.BrokerMessage;
import org.sibel.models.events.Event;

public class KafkaMessageProducerImpl implements KafkaMessageProducer {
    private static final Logger LOG = LogManager.getLogger();

    private KafkaProducer<String, String> kafkaProducer = null;

    private final Settings settings;
    private final Gson gson;

    @Inject
    public KafkaMessageProducerImpl(Settings settings, Gson gson) {
        this.settings = settings;
        this.gson = gson;
    }

    private KafkaProducer<String, String> createProducer() throws KafkaUnavailable {
        try {
            var bootstrapServers = String.format("%s:%s,", settings.KAFKA_HOST(), settings.KAFKA_PORT());
            Properties properties = new Properties();
            properties.setProperty(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
            properties.setProperty(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
            properties.setProperty(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

            if (!Objects.equals(settings.ENVIRONMENT(), "local")) {
                properties.setProperty(CommonClientConfigs.SECURITY_PROTOCOL_CONFIG, "SSL");
                properties.put(SslConfigs.SSL_KEYSTORE_TYPE_CONFIG, "PKCS12");
                properties.put(SslConfigs.SSL_KEYSTORE_LOCATION_CONFIG, settings.KAFKA_KEY_FILE_PATH());
                properties.put(SslConfigs.SSL_KEYSTORE_PASSWORD_CONFIG, settings.KAFKA_PASSWORD());
                properties.put(SslConfigs.SSL_TRUSTSTORE_TYPE_CONFIG, "PEM");
                properties.put(SslConfigs.SSL_TRUSTSTORE_CERTIFICATES_CONFIG, settings.KAFKA_CA_FILE());
            }
            return new KafkaProducer<>(properties);
        } catch (KafkaException e) {
            throw new KafkaUnavailable("Failed to create Kafka producer", e);
        }
    }

    private KafkaProducer<String, String> getProducer() throws KafkaUnavailable {
        if (kafkaProducer == null) {
            kafkaProducer = createProducer();
        }
        return kafkaProducer;
    }

    @Override
    public boolean isHealthy() {
        var healthy = false;
        if (kafkaProducer != null) {
            try {
                // Verify producer health by sending a message to the health check topic
                var record = new ProducerRecord<>(settings.KAFKA_TOPIC_HEALTH_CHECK(), "PING", "PING");
                kafkaProducer.send(record).get();
                healthy = true;
            } catch (Exception e) {
                LOG.error("Error connecting to kafka producer", e);
            }
        }

        return healthy;
    }

    @Override
    public void notify(BrokerMessage message, String topic, String key, List<RecordHeader> headers) {
        var record = new ProducerRecord<>(topic, key, gson.toJson(message));
        record.headers()
                .add(new RecordHeader(
                        KafkaHeaders.EVENT_TYPE, message.getEventType().getBytes()));
        if (headers != null) {
            headers.forEach(header -> record.headers().add(header));
        }
        try {
            getProducer().send(record);
        } catch (Exception e) {
            LOG.error("Error sending kafka message", e);
        }
    }

    @Override
    public void notify(Event event, String topic, String key, List<RecordHeader> headers) {
        var record = new ProducerRecord<>(topic, key, gson.toJson(event));
        record.headers()
                .add(new RecordHeader(
                        KafkaHeaders.EVENT_TYPE, event.getType().name().getBytes()));
        if (headers != null) {
            headers.forEach(header -> record.headers().add(header));
        }
        try {
            getProducer().send(record);
        } catch (Exception e) {
            LOG.error("Error sending kafka message", e);
        }
    }
}
