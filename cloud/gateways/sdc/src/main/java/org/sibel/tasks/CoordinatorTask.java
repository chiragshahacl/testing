package org.sibel.tasks;

import java.util.concurrent.Callable;

public interface CoordinatorTask extends Callable<Integer> {
    boolean isHealthy();
}
