package org.sibel.config;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
public @interface SettingValue {
    String variableName();

    String configurationName();

    boolean required() default true;

    String defaultValue() default "";

    String parserMethod() default "";
}
