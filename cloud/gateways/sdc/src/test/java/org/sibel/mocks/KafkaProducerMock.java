package org.sibel.mocks;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.fail;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.apache.commons.lang3.tuple.Pair;
import org.apache.kafka.common.header.internals.RecordHeader;
import org.sibel.models.BrokerMessage;
import org.sibel.models.events.Event;
import org.sibel.producers.KafkaMessageProducer;

public class KafkaProducerMock implements KafkaMessageProducer {
    // Topic -> Key -> MessageId -> Message with headers
    private final Map<String, Map<String, Map<String, Pair<BrokerMessage, List<RecordHeader>>>>> topics =
            new HashMap<>();

    // Topic -> Key -> Event id -> Event with headers
    private final Map<String, Map<String, Map<String, Pair<Event, List<RecordHeader>>>>> eventTopics = new HashMap<>();

    @Override
    public boolean isHealthy() {
        return true;
    }

    @Override
    public void notify(BrokerMessage message, String topic, String key, List<RecordHeader> headers) {
        var topicKey = getTopicKey(topic, key);
        topicKey.put(message.getMessageId(), Pair.of(message, headers));
    }

    @Override
    public void notify(Event event, String topic, String key, List<RecordHeader> headers) {
        var topicKey = getEventTopicKey(topic, key);
        topicKey.put(event.getId(), Pair.of(event, headers));
    }

    public void reset() {
        topics.clear();
        eventTopics.clear();
    }

    public void verifyMessageSent(String topicName, String key, BrokerMessage message, List<RecordHeader> headers) {
        var actualMessageWithHeaders = getBrokerMessage(topicName, key, message.getMessageId());
        if (actualMessageWithHeaders == null) {
            fail("No messages sent with topic: %s, key: %s, id: %s.\nThe following messages were sent:\n%s"
                    .formatted(topicName, key, message.getMessageId(), allMessagesToString()));
        }
        assertEquals(
                message,
                actualMessageWithHeaders.getLeft(),
                "Wrong body for message with topic: %s, key: %s, id: %s."
                        .formatted(topicName, key, message.getMessageId()));
        assertEquals(
                headers,
                actualMessageWithHeaders.getRight(),
                "Wrong headers for message with topic: %s, key: %s, id: %s."
                        .formatted(topicName, key, message.getMessageId()));
    }

    public void verifyNoMessagesSent() {
        if (!topics.isEmpty()) {
            fail("The following messages were sent:\n%s".formatted(allMessagesToString()));
        }
    }

    private Map<String, Pair<BrokerMessage, List<RecordHeader>>> getTopicKey(String topicName, String key) {
        var topic = getTopic(topicName);
        topic.putIfAbsent(key, new HashMap<>());
        return topic.get(key);
    }

    private Map<String, Map<String, Pair<BrokerMessage, List<RecordHeader>>>> getTopic(String topicName) {
        topics.putIfAbsent(topicName, new HashMap<>());
        return topics.get(topicName);
    }

    private Pair<BrokerMessage, List<RecordHeader>> getBrokerMessage(String topicName, String key, String messageId) {
        var topicKey = getTopicKey(topicName, key);
        return topicKey.get(messageId);
    }

    private String allMessagesToString() {
        var allMessages = new ArrayList<String>();
        topics.forEach((topicName, topic) -> {
            topic.forEach((key, topicKey) -> {
                topicKey.forEach((messageId, messageWithHeaders) -> {
                    allMessages.add("- Topic: %s / Key: %s / Message: %s / Headers: %s"
                            .formatted(topicName, key, messageWithHeaders.getLeft(), messageWithHeaders.getRight()));
                });
            });
        });
        return String.join("\n", allMessages);
    }

    public void verifyEventSent(String topicName, String key, Event event, List<RecordHeader> headers) {
        var actualEventWithHeaders = getEvent(topicName, key, event.getId());
        if (actualEventWithHeaders == null) {
            fail("No events sent with topic: %s, key: %s, id: %s.\nThe following events were sent:\n%s"
                    .formatted(topicName, key, event.getId(), allEventsToString()));
        }
        assertEquals(
                event,
                actualEventWithHeaders.getLeft(),
                "Wrong body for event with topic: %s, key: %s, id: %s.".formatted(topicName, key, event.getId()));
        assertEquals(
                headers,
                actualEventWithHeaders.getRight(),
                "Wrong headers for event with topic: %s, key: %s, id: %s.".formatted(topicName, key, event.getId()));
    }

    public void verifyNoEventsSent() {
        if (!eventTopics.isEmpty()) {
            fail("The following events were sent:\n%s".formatted(allEventsToString()));
        }
    }

    private Map<String, Pair<Event, List<RecordHeader>>> getEventTopicKey(String topicName, String key) {
        var topic = getEventTopic(topicName);
        topic.putIfAbsent(key, new HashMap<>());
        return topic.get(key);
    }

    private Map<String, Map<String, Pair<Event, List<RecordHeader>>>> getEventTopic(String topicName) {
        eventTopics.putIfAbsent(topicName, new HashMap<>());
        return eventTopics.get(topicName);
    }

    private Pair<Event, List<RecordHeader>> getEvent(String topicName, String key, String eventId) {
        var topicKey = getEventTopicKey(topicName, key);
        return topicKey.get(eventId);
    }

    private String allEventsToString() {
        var allEvents = new ArrayList<String>();
        eventTopics.forEach((topicName, topic) -> {
            topic.forEach((key, topicKey) -> {
                topicKey.forEach((eventId, eventWithHeaders) -> {
                    allEvents.add("- Topic: %s / Key: %s / Event: %s / Headers: %s"
                            .formatted(topicName, key, eventWithHeaders.getLeft(), eventWithHeaders.getRight()));
                });
            });
        });
        return String.join("\n", allEvents);
    }
}
