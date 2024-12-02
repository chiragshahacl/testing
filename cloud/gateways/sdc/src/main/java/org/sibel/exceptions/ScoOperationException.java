package org.sibel.exceptions;

public class ScoOperationException extends Exception {
    public ScoOperationException(String message) {
        super(message);
    }

    public ScoOperationException(String message, Throwable cause) {
        super(message, cause);
    }
}
