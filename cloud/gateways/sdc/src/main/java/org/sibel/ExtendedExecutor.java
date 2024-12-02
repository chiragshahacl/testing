package org.sibel;

import java.util.concurrent.*;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class ExtendedExecutor extends ThreadPoolExecutor {
    private static final Logger LOG = LogManager.getLogger();

    private Throwable error = null;

    public ExtendedExecutor() {
        super(0, Integer.MAX_VALUE, 5L, TimeUnit.MINUTES, new SynchronousQueue<>());
    }

    public boolean hasError() {
        return error != null;
    }

    public String getErrorMessage() {
        return hasError() ? error.toString() : "";
    }

    @Override
    protected void afterExecute(Runnable r, Throwable t) {
        super.afterExecute(r, t);

        var taskError = t;
        if (taskError == null && r instanceof Future<?>) {
            try {
                var future = (Future<?>) r;
                if (future.isDone()) {
                    future.get();
                }
            } catch (CancellationException ce) {
                taskError = ce;
            } catch (ExecutionException ee) {
                taskError = ee.getCause();
            } catch (InterruptedException ie) {
                Thread.currentThread().interrupt();
            }
        }
        if (taskError != null) {
            LOG.error("Task ended with an error", taskError);
            error = taskError;
        }
    }
}
