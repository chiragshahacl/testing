package org.sibel.exceptions;

public class ProcessingError extends Exception {
    public ProcessingError(String message) {
        super(message);
    }

    public ProcessingError(String message, Throwable cause) {
        super(message, cause);
    }
}
