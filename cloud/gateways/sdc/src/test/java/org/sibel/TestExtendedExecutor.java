package org.sibel;

import static org.junit.jupiter.api.Assertions.*;

import java.util.concurrent.ExecutionException;
import org.junit.jupiter.api.Test;

class TestExtendedExecutor {
    @Test
    void testCallableErrorsCapture() throws InterruptedException {
        try (var executor = new ExtendedExecutor()) {
            var expectedException = new RuntimeException("Test Error!");

            var taskFuture = executor.submit(() -> {
                throw expectedException;
            });

            try {
                taskFuture.get();
            } catch (ExecutionException e) {
                assertEquals(e.getCause(), expectedException);
            }

            // Need to wait for the future to finish
            Thread.sleep(100);

            assertTrue(executor.hasError());
            assertEquals(executor.getErrorMessage(), expectedException.toString());
        }
    }
}
