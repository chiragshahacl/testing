package org.sibel.config;

import org.apache.commons.configuration2.PropertiesConfiguration;
import org.apache.commons.configuration2.builder.FileBasedConfigurationBuilder;
import org.apache.commons.configuration2.builder.fluent.Parameters;
import org.apache.commons.configuration2.ex.ConfigurationException;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class EnvironmentAdapterImpl implements EnvironmentAdapter {
    private static final Logger LOG = LogManager.getLogger();

    private PropertiesConfiguration configuration = null;

    public EnvironmentAdapterImpl() {
        var params = new Parameters();
        var builder = new FileBasedConfigurationBuilder<>(PropertiesConfiguration.class)
                .configure(params.properties().setFileName("config.properties"));
        try {
            configuration = builder.getConfiguration();
        } catch (ConfigurationException exception) {
            LOG.warn("Error loading config.properties.", exception);
        }
    }

    @Override
    public String getValue(String envKey, String configKey) {
        var envValue = System.getenv(envKey);
        var configValue = configuration != null ? configuration.getString(configKey) : null;
        return envValue != null ? envValue : configValue;
    }
}
