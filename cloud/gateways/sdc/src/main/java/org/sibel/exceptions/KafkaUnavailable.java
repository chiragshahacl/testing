package org.sibel.exceptions;

public class KafkaUnavailable extends Exception {
    public KafkaUnavailable(String message, Throwable cause) {
        super(message, cause);
    }

    public KafkaUnavailable(String message) {
        super(message);
    }
}
