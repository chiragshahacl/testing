package org.sibel.config;

public interface EnvironmentAdapter {
    String getValue(String envKey, String configKey);
}
