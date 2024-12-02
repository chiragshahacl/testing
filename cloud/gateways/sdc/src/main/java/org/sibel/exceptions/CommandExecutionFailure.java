package org.sibel.exceptions;

public class CommandExecutionFailure extends Exception {
    public CommandExecutionFailure(String message) {
        super(message);
    }

    public CommandExecutionFailure(String message, Throwable cause) {
        super(message, cause);
    }
}
