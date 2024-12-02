package org.sibel.config;

import com.google.inject.TypeLiteral;
import com.google.inject.spi.TypeEncounter;
import com.google.inject.spi.TypeListener;
import java.lang.reflect.Field;

public class SettingsTypeListener implements TypeListener {
    @Override
    public <I> void hear(TypeLiteral<I> type, TypeEncounter<I> encounter) {
        Class<?> clazz = type.getRawType();
        while (clazz != null) {
            for (Field field : clazz.getDeclaredFields()) {
                if (field.isAnnotationPresent(SettingValue.class)) {
                    encounter.register(new SettingsMemberInjector<I>(clazz, field, new EnvironmentAdapterImpl()));
                }
            }
            clazz = clazz.getSuperclass();
        }
    }
}
