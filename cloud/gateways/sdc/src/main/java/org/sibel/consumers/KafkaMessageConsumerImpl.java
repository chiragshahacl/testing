package org.sibel.consumers;

import com.google.inject.Inject;
import java.time.Duration;
import java.util.*;
import org.apache.kafka.clients.CommonClientConfigs;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.KafkaException;
import org.apache.kafka.common.config.SslConfigs;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.config.Settings;
import org.sibel.exceptions.KafkaUnavailable;

public class KafkaMessageConsumerImpl implements KafkaMessageConsumer {
    private static final int HEALTH_CHECK_TIMEOUT = 500;
    private static final Logger LOG = LogManager.getLogger();

    private KafkaConsumer<String, String> kafkaConsumer = null;
    private KafkaConsumer<String, String> kafkaHealthCheckConsumer = null;

    private final Settings settings;

    @Inject
    public KafkaMessageConsumerImpl(Settings settings) {
        this.settings = settings;
    }

    private KafkaConsumer<String, String> createConsumer() throws KafkaUnavailable {
        try {
            var properties = new Properties();
            var bootstrapServers = String.format("%s:%s,", this.settings.KAFKA_HOST(), this.settings.KAFKA_PORT());
            properties.setProperty(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
            properties.setProperty(
                    ConsumerConfig.GROUP_ID_CONFIG, UUID.randomUUID().toString());
            properties.setProperty(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
            properties.setProperty(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
            if (!Objects.equals(this.settings.ENVIRONMENT(), "local")) {
                properties.setProperty(CommonClientConfigs.SECURITY_PROTOCOL_CONFIG, "SSL");
                properties.put(SslConfigs.SSL_KEYSTORE_TYPE_CONFIG, "PKCS12");
                properties.put(SslConfigs.SSL_KEYSTORE_LOCATION_CONFIG, settings.KAFKA_KEY_FILE_PATH());
                properties.put(SslConfigs.SSL_KEYSTORE_PASSWORD_CONFIG, settings.KAFKA_PASSWORD());
                properties.put(SslConfigs.SSL_TRUSTSTORE_TYPE_CONFIG, "PEM");
                properties.put(SslConfigs.SSL_TRUSTSTORE_CERTIFICATES_CONFIG, settings.KAFKA_CA_FILE());
            }
            return new KafkaConsumer<>(properties);
        } catch (KafkaException e) {
            throw new KafkaUnavailable("Failed to create Kafka consumer", e);
        }
    }

    private KafkaConsumer<String, String> getConsumer() throws KafkaUnavailable {
        if (kafkaConsumer == null) {
            kafkaConsumer = createConsumer();
        }
        return kafkaConsumer;
    }

    @Override
    public boolean isHealthy() {
        try {
            if (kafkaHealthCheckConsumer == null) {
                kafkaHealthCheckConsumer = createConsumer();
            }
            kafkaHealthCheckConsumer.subscribe(Collections.singletonList(settings.KAFKA_TOPIC_HEALTH_CHECK()));
            var record = kafkaHealthCheckConsumer.poll(Duration.ofMillis(HEALTH_CHECK_TIMEOUT));
            return record != null && !record.isEmpty();
        } catch (Exception e) {
            LOG.error("Health check failed", e);
        }
        return false;
    }

    @Override
    public void subscribeToTopic(String topic) throws KafkaUnavailable {
        try {
            getConsumer().subscribe(Collections.singletonList(topic));
        } catch (KafkaUnavailable e) {
            throw e;
        } catch (Exception e) {
            throw new KafkaUnavailable("Failed to subscribe to topic", e);
        }
    }

    @Override
    public ConsumerRecords<String, String> poll(Duration duration) throws KafkaUnavailable {
        try {
            return getConsumer().poll(duration);
        } catch (KafkaUnavailable e) {
            throw e;
        } catch (Exception e) {
            throw new KafkaUnavailable("Failed poll messages", e);
        }
    }
}
