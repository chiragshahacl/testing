package org.sibel.config;

import com.google.inject.MembersInjector;
import java.lang.reflect.Field;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.exceptions.SettingsException;

public class SettingsMemberInjector<T> implements MembersInjector<T> {
    private static final Logger LOG = LogManager.getLogger();

    private final Class<?> clazz;
    private final Field field;
    private final EnvironmentAdapter env;
    private final SettingValue annotation;

    public SettingsMemberInjector(Class<?> clazz, Field field, EnvironmentAdapter env) {
        this.clazz = clazz;
        this.field = field;
        this.env = env;
        annotation = field.getAnnotation(SettingValue.class);
    }

    @Override
    public void injectMembers(T instance) {
        try {
            field.set(instance, getFieldValue());
        } catch (IllegalAccessException | SettingsException e) {
            LOG.error("Error loading setting value.", e);
            throw new RuntimeException(e);
        }
    }

    private Object getFieldValue() throws SettingsException {
        var rawValue = env.getValue(annotation.variableName(), annotation.configurationName());
        if (annotation.required() && annotation.defaultValue().isBlank() && rawValue == null) {
            throw new SettingsException("Required setting not set %s (%s)."
                    .formatted(annotation.variableName(), annotation.configurationName()));
        }

        if (annotation.defaultValue().isBlank() && (rawValue == null || rawValue.isBlank())) {
            return null;
        } else if (rawValue == null || rawValue.isBlank()) {
            rawValue = annotation.defaultValue();
        }

        try {
            var fieldType = field.getType();
            if (!annotation.parserMethod().isBlank()) {
                try {
                    var parserMethod = clazz.getDeclaredMethod(annotation.parserMethod(), String.class);
                    return parserMethod.invoke(null, rawValue.trim());
                } catch (Exception e) {
                    throw new SettingsException(
                            "No suitable parser method \"%s\" found.".formatted(annotation.parserMethod()), e);
                }
            } else if (fieldType == String.class) {
                return rawValue.trim();
            } else if (Integer.class == fieldType || int.class == fieldType) {
                return Integer.parseInt(rawValue.trim());
            } else if (Boolean.class == fieldType || boolean.class == fieldType) {
                return Boolean.parseBoolean(rawValue.trim().toLowerCase());
            } else {
                throw new SettingsException("Unknown setting type %s found for setting %s (%s)."
                        .formatted(fieldType.getName(), annotation.variableName(), annotation.configurationName()));
            }
        } catch (SettingsException e) {
            throw e;
        } catch (Exception e) {
            throw new SettingsException(
                    "Unable to parse setting value for variable %s (%s)."
                            .formatted(annotation.variableName(), annotation.configurationName()),
                    e);
        }
    }
}
