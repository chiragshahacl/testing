package org.sibel.utils;

import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.core.config.Configurator;
import org.sibel.config.Settings;
import org.sibel.di.ConsumerModule;

/**
 * This class provides the configuration used for the consumer instance.
 * <p>
 * Overwriting configuration steps allows customizing the behavior of the framework through
 * injection.
 */
public class ConsumerUtil extends BaseUtil {
    public ConsumerUtil(String[] args) {
        super(args);

        injector = injector.createChildInjector(new ConsumerModule());

        var settings = injector.getInstance(Settings.class);
        Level logLevel = Level.getLevel(settings.LOG_LEVEL());
        Configurator.reconfigure(localLoggerConfig(logLevel));
    }
}
