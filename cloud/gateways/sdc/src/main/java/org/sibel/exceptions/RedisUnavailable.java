package org.sibel.exceptions;

public class RedisUnavailable extends RuntimeException {
    public RedisUnavailable(String message, Throwable cause) {
        super(message, cause);
    }

    public RedisUnavailable(String message) {
        super(message);
    }
}
